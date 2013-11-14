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
        print 'container post'
        container = self.container_name
        base_dir = '/var/lib/mstore'
        bucket_path = os.path.join(base_dir, container)
        print 'mkdirs'
        print bucket_path
       
        try:
            os.mkdirs(bucket_path)
        except:
            print 'error'
            
        return 200

    def hello(self):
        print 'hello world'
