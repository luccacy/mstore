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
from eventlet import sleep, Timeout

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
        pass
        
    def _exec(self, *cmd, **kwargs):
        return processutils.execute(*cmd, **kwargs)

    def POST(self, req):
        print 'compute post'
        return HTTPOk(request=req)

    def GET(self, req):
        print 'GET'
        pass
        
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
        
