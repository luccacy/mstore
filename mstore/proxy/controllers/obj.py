# Copyright (c) 2010-2012 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# NOTE: mstore_conn
# You'll see mstore_conn passed around a few places in this file. This is the
# source httplib connection of whatever it is attached to.
#   It is used when early termination of reading from the connection should
# happen, such as when a range request is satisfied but there's still more the
# source connection would like to send. To prevent having to read all the data
# that could be left, the source connection can be .close() and then reads
# commence to empty out any buffers.
#   These shenanigans are to ensure all related objects can be garbage
# collected. We've seen objects hang around forever otherwise.

import itertools
import mimetypes
import re
import time
from datetime import datetime
from urllib import unquote, quote
from hashlib import md5
import os
from mstore.common import fileutils
from mstore.common import cfg
from mstore.common import logger
from mstore.common import processutils
from mstore.common import http
from mstore.common.utils import ContextPool
from mstore.common.bufferedhttp import http_connect 
from mstore.common.exception import ChunkWriteTimeout,ChunkReadTimeout
from eventlet import Timeout
from eventlet.queue import Queue
import eventlet
from eventlet import spawn_n

from mstore.common.swob import HTTPOk, HTTPAccepted, HTTPBadRequest, HTTPNotFound, \
    HTTPPreconditionFailed, HTTPRequestEntityTooLarge, HTTPRequestTimeout, \
    HTTPServerError, HTTPServiceUnavailable, Request, Response, \
    HTTPClientDisconnect

core_opts = [
    cfg.StrOpt('base_dir', default='/var/lib/mstore',
                help=('where the mstore server store data')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

LOG = logger.get_logger(__name__)

class ResponseBodyIterator(object):
    """A class that acts as an iterator over an HTTP response."""

    def __init__(self, resp):
        self.resp = resp

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        chunk = self.resp.read(1024)
        if chunk:
            return chunk
        else:
            raise StopIteration()

class ObjectController(object):
    """WSGI controller for object requests."""
    server_type = 'Object'

    def __init__(self, app, account_name, container_name, object_name,
                 **kwargs):
        
        self.account_name = unquote(account_name)
        self.container_name = unquote(container_name)
        self.object_name = unquote(object_name)
        self.base_dir = CONF.base_dir
        endpoint = 'http://10.12.13.16:9898'
        kwargs1 = {'ssl_compression': True, 'cert_file': None,
        'token':'8ba9eb7c22934f26bd21ee77e4b86a3c', 'timeout': 600, 'cacert': '', 'key_file': None, 'insecure': False}
        self.client = http.HTTPClient(endpoint, **kwargs1)
        
    def _exec(self, *cmd, **kwargs):
        return processutils.execute(*cmd, **kwargs)
    
    def _send_file(self, conn, path):
        """Method for a file PUT coro"""
        while True:
            chunk = conn.queue.get()
            if not conn.failed:
                try:
                    with ChunkWriteTimeout(600):
                        conn.send(chunk)
                except (Exception, ChunkWriteTimeout):
                    conn.failed = True
                    print 'failed to connect'
            conn.queue.task_done()

    def POST(self, req):
        
        print 'proxy obj post'
        
        headers = {}
        headers['Content-Type']='application/octet-stream'
        
        chunked=True

        reader = req.environ['wsgi.input'].read
        data_source = iter(lambda: reader(1024), '')
        conn = http_connect('10.12.13.16', '9898', 'dev', 'part', 'POST', '/test/path', headers=headers)
        try:
            pool = eventlet.GreenPool(10)
            if pool:
                conn.failed = False
                conn.queue = Queue(10)
                pool.spawn(self._send_file, conn, req.path)
                
                while True:
                    with ChunkReadTimeout(600):
                        try:
                            chunk = next(data_source)
                        except StopIteration:
                            if chunked:
                                [conn.queue.put('0\r\n\r\n')]
                            break
                        
                    if not conn.failed:
                            conn.queue.put(
                                '%x\r\n%s\r\n' % (len(chunk), chunk)
                                if chunked else chunk)
                    else:
                        print 'failed to connect server'
                        
            return HTTPOk(request=req, status=200)
                        
                    
        except ChunkReadTimeout, err:
            print 'timeout1'
            return HTTPRequestTimeout(request=req)
        except (Exception, Timeout):
            print 'timeout2'
            return HTTPClientDisconnect(request=req)
        
    def _make_app_iter_reader(self, source, queue, logger_thread_locals):
        """
        Reads from the source and places data in the queue. It expects
        something else be reading from the queue and, if nothing does within
        self.app.client_timeout seconds, the process will be aborted.

        :param node: The node dict that the source is connected to, for
                     logging/error-limiting purposes.
        :param source: The httplib.Response object to read from.
        :param queue: The eventlet.queue.Queue to place read source data into.
        :param logger_thread_locals: The thread local values to be set on the
                                     self.app.logger to retain transaction
                                     logging information.
        """
        success = True
        print '_make_app_iter_reader'
        try:
            try:
                while True:
                    with ChunkReadTimeout(600):
                        chunk = source.read(1024)
                        print chunk
                    if not chunk:
                        break
                    queue.put(chunk, timeout=self.app.client_timeout)
            except (Exception, Timeout):
                LOG.error(('Trying to read during GET'))
                success = False
        finally:
            # Ensure the queue getter gets a terminator.
            queue.resize(2)
            queue.put(success)
            

    def _make_app_iter(self, source):
        """
        Returns an iterator over the contents of the source (via its read
        func).  There is also quite a bit of cleanup to ensure garbage
        collection works and the underlying socket of the source is closed.

        :param source: The httplib.Response object this iterator should read
                       from.
        :param node: The node the source is reading from, for logging purposes.
        """
        try:
            # Spawn reader to read from the source and place in the queue.
            # We then drop any reference to the source or node, for garbage
            # collection purposes.
            print '_make_app_iter'
            queue = Queue(1)
            spawn_n(self._make_app_iter_reader, source, queue,
                    100)
            source = None
            while True:
                chunk = queue.get(timeout=1000)
                if isinstance(chunk, bool):  # terminator
                    success = chunk
                    if not success:
                        raise Exception(('Failed to read all data'
                                          ' from the source'))
                    break
                yield chunk
        except (Timeout):
            LOG.warn(_('Client disconnected on read'))
        except Exception:
            LOG.exception(_('Trying to send to client'))
            raise
        
    def GET(self, req):
        headers={}
        headers['Transfer-Encoding']='chunked'
        
        conn = http_connect('10.12.13.16', '9898', 'dev', 'part', 'GET', '/test/path', headers=headers)
        possible_source = conn.getresponse()
        res = Response(request=req, conditional_response=True)
        res.app_iter = ResponseBodyIterator(possible_source)
        res.accept_ranges = 'bytes'
        res.content_length = possible_source.getheader('Content-Length')
        res.content_type = possible_source.getheader('Content-Type')
        
        return res

        
    def GET1(self, req):
        
        container_path = os.path.join(self.base_dir, self.container_name)
        object_path = os.path.join(container_path, self.object_name)
        
        if not os.path.exists(object_path):
            LOG.error('failed to find object : %s', object_path)
            raise
        
        real_object = None
        if self.object_name == 'base' or self.object_name == 'result':
            real_object = os.path.join(object_path, '.tar.gz')
            if not os.path.exists(real_object):
                cmd = 'tar czf %s %s' % (real_object, object_path)
                self._exec(cmd, shell=True)               
        else:
            raise
        
        def file_iter(filename):
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(1024)
                        if chunk:
                            yield chunk
                        else:
                            break
                    
        return Response(request=req,
                        content_type='application/octec-stream',
                        app_iter=file_iter(real_object))
