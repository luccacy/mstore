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

from mstore.common.swob import HTTPAccepted, HTTPBadRequest, HTTPNotFound, \
    HTTPPreconditionFailed, HTTPRequestEntityTooLarge, HTTPRequestTimeout, \
    HTTPServerError, HTTPServiceUnavailable, Request, Response, \
    HTTPClientDisconnect


class ObjectController(object):
    """WSGI controller for object requests."""
    server_type = 'Object'

    def __init__(self, app, account_name, container_name, object_name,
                 **kwargs):
        
        self.account_name = unquote(account_name)
        self.container_name = unquote(container_name)
        self.object_name = unquote(object_name)

    def POST(self, req):
        print 'object write'
        data = req.body
        base_dir = '/var/lib/mstore'
        container_path = os.path.join(base_dir, self.container_name)
        obj_path = os.path.join(container_path, self.object_name)
        
        #with open(obj_path, 'wb') as wfile:
        #    wfile.write(data)

        '''
        headers={}
        headers['Content-Type']='application/json'
        body={'status':'ok'}
        resp = Response(request=req, conditional_response=True,
                status=200, body=json.dumps(body))
        return resp

        return HTTPBadRequest(request=req,content_type='text/plain',
                body='bad')
        return req.get_response(resp) 
        return Response(request=req,
                content_type='application/json',
                body={'status':'ok'})
        '''
        return Response(request=req,
                content_type='application/octet-stream',
                app_iter = req.body)
