import inspect
import logging as std_logging
import os
import random
import time
#from mstore.paste.deploy.loadwsgi import loadapp
#from paste import deploy

import wsgi
from mstore.common import cfg
from mstore.common import logger
from threading import Thread, Event, Lock

from mstore import router
from mstore.proxy import server as appserver

core_opts = [
    cfg.StrOpt('listen_addr', default='0.0.0.0',
                help=('The mstore server listen address')),
    cfg.StrOpt('port', default='7878',
                help=('The mstore server listen port')),
    cfg.StrOpt('paste_file', default='c://etc/mstore/api-paste.ini',
                help=('The mstore server paste file')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

LOG = logger.get_logger(__name__)


class WsgiService(object):
    """Base class for WSGI based services.

    For each api you define, you must also define these flags:
    :<api>_listen: The address on which to listen
    :<api>_listen_port: The port on which to listen

    """

    def __init__(self, app_name):
        self.app_name = app_name
        self.wsgi_app = None

    def start(self):
        self.wsgi_app = _run_wsgi(self.app_name)
        
    def wait(self):
        self.wsgi_app.wait()


class DeployApiService(WsgiService):
        
    @classmethod
    def create(cls):
        app_name = "mstore"
    
        # Setup logging early, supplying both the CLI options and the
        # configuration mapping from the config file
        # We only update the conf dict for the verbose and debug
        # flags. Everything else must be set up in the conf file...
        # Log the options used when starting if we're in debug mode...
                                                                                                                                             
        # Dump the initial option values
        service = cls(app_name)
        return service


def serve_wsgi(cls):
    try:
        service = cls.create()
    except Exception:
        LOG.exception(('In WsgiService.create()'))
        raise 
        
    service.start()
        
    return service

def _run_wsgi(app_name):

    configfile=CONF.paste_file
    port = CONF.port
    listen_addr = CONF.listen_addr
    appname="mstore"
 
    global_config = {'__file__': 'c:\\etc\\mstore\\api-paste.ini', 'here': 'c:\\etc\\mstore'}
    local_config = {'version': '1.0.0'}
    #app = router.APIRouter.factory(global_config, **local_config)
    app = appserver.app_factory(global_config, **local_config)

    if not app:
        LOG.error(('No known API applications configured.'))
        return

    server = wsgi.Server(appname)    
    server.start(app, port, listen_addr)
    LOG.info('start server')

    return server
