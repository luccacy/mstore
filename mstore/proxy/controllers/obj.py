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

    def POST(self, req):
        
        print 'proxy obj post'
        url = "/v1/images/metadata"
        body = {"image_meta":
                {"status":
                    "active", "name": "cir", "container_format": "ovf", "disk_format":
                    "qcow2", "protected": False, "is_public":  True, "checksum":
                    "8abc2460f14e009d13d9861f10f5efac", "size": 11141121}}
        resp, body = self.client.json_request('POST', url, body=body)
        print resp
        print body

        
    def GET(self, req):
        
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
