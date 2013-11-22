# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
# Copyright 2011 Piston Cloud Computing, Inc.

# All Rights Reserved.
"""
OpenStack Client interface. Handles the REST calls and responses.
"""

import logging
import os
import sys
import time
import urlparse

import pkg_resources
import requests

try:
    import json
except ImportError:
    import simplejson as json

# Python 2.5 compat fix
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl


class HTTPClient(object):

    USER_AGENT = 'python-client'

    def __init__(self, server_ip=None, server_port=None):

        self.management_url = 'http://%s:%s' % (server_ip, server_port)

    def set_management_url(self, url):
        self.management_url = url

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        #kwargs['headers']['User-Agent'] = self.USER_AGENT
        #kwargs['headers']['Accept'] = 'application/json'
        #kwargs['headers']['X-Auth-Project-Id'] = 'admin'
        kwargs['headers']['Accept-Encoding'] = 'identity'
        kwargs['headers']['Content-Type'] = 'application/json'
        kwargs['headers']['X-Auth-Token'] = '3d16e2a3d0df445aa425b9a49429431b'
        
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']

        resp = requests.request(
            method,
            url,
            **kwargs)

        if resp.text:
            if resp.status_code == 400:
                if ('Connection refused' in resp.text or
                    'actively refused' in resp.text):
                    raise "connection refused!"
            try:
                body = json.loads(resp.text)
            except ValueError:
                pass
                body = None
        else:
            body = None

        #if resp.status_code >= 400:
         #   raise "response >= 400" 

        return resp, body

    def _cs_request(self, url, method, **kwargs):
        resp, body = self.request(self.management_url + url, method,
                                        **kwargs)
        return resp, body

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)
