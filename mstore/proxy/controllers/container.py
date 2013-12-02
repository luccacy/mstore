from urllib import unquote

from mstore.common.swob import HTTPBadRequest, HTTPForbidden, \
    HTTPNotFound
import os

class ContainerController(object):
    """WSGI controller for container requests"""
    server_type = 'Container'

    # Ensure these are all lowercase
    pass_through_headers = ['x-container-read', 'x-container-write',
                            'x-container-sync-key', 'x-container-sync-to',
                            'x-versions-location']

    def __init__(self, app, account_name, container_name, **kwargs):
        self.account_name = unquote(account_name)
        self.container_name = unquote(container_name)

    def POST(self, req):
        pass