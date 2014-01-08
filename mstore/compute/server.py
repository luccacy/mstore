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
import traceback
from mstore.common import fileutils
from mstore.common import cfg
from mstore.common import logger
from mstore.common import processutils
from mstore.common.utils import split_path
from eventlet import sleep, Timeout
from mstore.compute import taskflow
from mstore.compute import task
from mstore.compute import adpter

from mstore.common.swob import HTTPAccepted, HTTPBadRequest, HTTPCreated, \
    HTTPInternalServerError, HTTPNoContent, HTTPNotFound, HTTPNotModified, \
    HTTPPreconditionFailed, HTTPRequestTimeout, HTTPUnprocessableEntity, \
    HTTPClientDisconnect, HTTPMethodNotAllowed, Request, Response, UTC, \
    HTTPInsufficientStorage, HTTPForbidden, multi_range_iterator, \
    HeaderKeyDict, HTTPOk

core_opts = [
    cfg.StrOpt('base_dir', default='/var/lib/mstore',
                help=('where the mstore server store data')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

LOG = logger.get_logger(__name__)


class ComputeController(object):
    """WSGI controller for object requests."""
    server_type = 'Object'

    def __init__(self, conf):
        self.allowed_methods = ['DELETE', 'PUT', 'HEAD', 'GET', 'REPLICATE', 'POST']
        self.base_dir = '/var/lib/mstore'
        adpter.load_all_adapters(adpter.__path__[0])
        
    def _get_parts(self, path):
        version, account, container, obj = split_path(path, 1, 4, True)
        d = dict(version=version,
                 account_name=account,
                 container_name=container,
                 object_name=obj)
        return d
    
    def _exec(self, *cmd, **kwargs):
        return processutils.execute(*cmd, **kwargs)

    def POST(self, req):
        
        print 'compute post'
        print req.body
        
        return Response(request=req, status=200)
        parts = self._get_parts(req.path)
        version = parts.get('version', None)
        account_name = parts.get('account_name', None)
        container_name = parts.get('container_name', None)
        object_zip_name = parts.get('object_name', None)
        object_name, ext_name = os.path.splitext(os.path.split(object_zip_name)[-1])
        
        container_dir = os.path.join(self.base_dir, container_name)
        object_zip_path = os.path.join(container_dir, object_zip_name)
        object_unzip_path = os.path.join(container_dir, object_name)
        
        
        with open(object_zip_path, 'wb') as f:
            for CHUNK in req.body:
                f.write(CHUNK)
                
        if object_zip_path:
            self._exec('unzip -n %s -d %s' % (object_zip_path, container_dir), shell=True)
        
        object_result_name = object_name + 'result'
        object_result_path = os.path.join(container_dir, object_result_name)
        
        _task_flow = taskflow.TaskFlow()
        
        for img in os.listdir(object_unzip_path):
            if img.endswith('jpg') or img.endswith('jpeg'):
                img_src = os.path.join(object_unzip_path, img)
                img_dst = os.path.join(object_result_path, img)
                
                _task = task.Rgb2grayTask(img_src, img_dst)
                _task_flow.add(_task)
                
        _task_flow.run()
        
        return HTTPOk(request=req)

    def PUT(self, req):
        return Response(request = req, 
                        status = 200,
                        body = 'ready')
        
    def GET(self,req):
        print 'get object'
        
        obj_path = '/var/lib/mstore/localfs.py'
        
        def file_iter(filename):
            
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if chunk:
                        yield chunk
                    else:
                        break
                    
        return Response(request=req,
                        content_type='application/octec-stream',
                        app_iter=file_iter(obj_path)) 
        
        
    def __call__(self, env, start_response):
        """WSGI Application entry point for the Swift Object Server."""
        start_time = time.time()
        req = Request(env)
        
        def check_utf8(string):
            """
            Validate if a string is valid UTF-8 str or unicode and that it
            does not contain any null character.
        
            :param string: string to be validated
            :returns: True if the string is valid utf-8 str or unicode and
                      contains no null characters, False otherwise
            """
            if not string:
                return False
            try:
                if isinstance(string, unicode):
                    string.encode('utf-8')
                else:
                    string.decode('UTF-8')
                return '\x00' not in string
            # If string is unicode, decode() will raise UnicodeEncodeError
            # So, we should catch both UnicodeDecodeError & UnicodeEncodeError
            except UnicodeError:
                return False

        if not check_utf8(req.path_info):
            res = HTTPPreconditionFailed(body='Invalid UTF8 or contains NULL')
        else:
            try:
                # disallow methods which have not been marked 'public'
                try:
                    method = getattr(self, req.method)
                    if req.method not in self.allowed_methods:
                        raise AttributeError('Not allowed method.')
                except AttributeError:
                    res = HTTPMethodNotAllowed()
                else:
                    res = method(req)
            except (Exception, Timeout):
                self.logger.exception(_(
                    'ERROR __call__ error with %(method)s'
                    ' %(path)s '), {'method': req.method, 'path': req.path})
                res = HTTPInternalServerError(body=traceback.format_exc())
        return res(env, start_response)
    
    
def app_factory(global_conf, **local_conf):
    """paste.deploy app factory for creating WSGI object server apps"""
    conf = global_conf.copy()
    conf.update(local_conf)
    return ComputeController(conf)
        
