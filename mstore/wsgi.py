"""
Utility methods for working with WSGI servers
"""
import socket
import sys
from xml.etree import ElementTree as etree
from xml.parsers import expat

import eventlet.wsgi
eventlet.patcher.monkey_patch(all=False, socket=True)
import webob.dec
import webob.exc
import routes.middleware

from mstore.common import jsonutils
from mstore.common import timeutils
from mstore.common import logger
from mstore.common import exception 

LOG = logger.get_logger(__name__)

def run_server(application, port):
    """Run a WSGI server with the given application."""
    sock = eventlet.listen(('0.0.0.0', port))
    eventlet.wsgi.server(sock, application)

class Server(object):
    """Server class to manage multiple WSGI sockets and applications."""

    def __init__(self, name, threads=10):       
        self.pool = eventlet.GreenPool(threads)
        self.name = name

    def start(self, application, port, host='0.0.0.0', backlog=128):
        """Run a WSGI server with the given application."""
        self._host = host
        self._port = port
    
        # TODO(dims): eventlet's green dns/socket module does not actually
        # support IPv6 in getaddrinfo(). We need to get around this in the
        # future or monitor upstream for a fix
        try:
            info = socket.getaddrinfo(self._host,
                                      self._port,
                                      socket.AF_UNSPEC,
                                      socket.SOCK_STREAM)[0]
            family = info[0]
            bind_addr = info[-1]      
                                      
            self._socket = eventlet.listen(bind_addr,                                                                                        
                                           family=family,
                                           backlog=backlog)
        except:                       
            LOG.error("unable to bind the port : %s, maybe it's in use", self._port)
            sys.exit(1)                    
        
        self._server = self.pool.spawn(self._run, application, self._socket)
                          
    @property
    def host(self):       
        return self._socket.getsockname()[0] if self._socket else self._host
            
    @property
    def port(self):
        return self._socket.getsockname()[1] if self._socket else self._port
    
    def stop(self):
        self._server.kill()
        
    def wait(self):
        """Wait until all servers have completed running."""
        try:
            self.pool.waitall()
        except KeyboardInterrupt:
            pass
        
    def _run(self, application, socket):                                                                                                     
        """Start a WSGI server in a new green thread."""
        eventlet.wsgi.server(socket, application, custom_pool=self.pool)

class Router(object):
    """ 
    WSGI middleware that maps incoming requests to WSGI apps.
    """                                                                                                                              
    
    @classmethod
    def factory(cls, global_config, **local_config):
        """
        Returns an instance of the WSGI Router class
        """
        return cls()
        
    def __init__(self, mapper):
        self.map = mapper
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.map)

    @webob.dec.wsgify
    def __call__(self, req):
        """                                               
        Route the incoming request to a controller based on self.map.
        If no match, return a 404.
        """
        return self._router                               

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
        """                                                                                                                          
        Called by self._router after matching the incoming request to a route
        and putting the information into req.environ.  Either returns 404
        or the routed WSGI app's response.
        """
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app

class Request(webob.Request):

    def best_match_content_type(self):
        """Determine the most acceptable content-type.

        Based on:
            1) URI extension (.json/.xml)                                                                                            
            2) Content-type header
            3) Accept* headers
        """ 
        # First lookup http request path
        parts = self.path.rsplit('.', 1)
        if len(parts) > 1:
            _format = parts[1]
            if _format in ['json', 'xml']:
                return 'application/{0}'.format(_format)
            
        #Then look up content header
        type_from_header = self.get_content_type()
        if type_from_header:
            return type_from_header
        ctypes = ['application/json', 'application/xml']
            
        #Finally search in Accept-* headers
        bm = self.accept.best_match(ctypes)
        return bm or 'application/json'

class ActionDispatcher(object):
    """Maps method name to local methods through action name."""

    def dispatch(self, *args, **kwargs):
        """Find and call local method."""
        action = kwargs.pop('action', 'default')
        action_method = getattr(self, str(action), self.default)
        return action_method(*args, **kwargs)
        
    def default(self, data):
        raise exception.NotImplementedError()

class TextDeserializer(ActionDispatcher):
    """Default request body deserialization"""

    def deserialize(self, datastring, action='default'):
        return self.dispatch(datastring, action=action)
                                                                                                                                               
    def default(self, datastring):
        return {}

class JSONDeserializer(TextDeserializer):
    
    def _from_json(self, datastring):
        try:
            return jsonutils.loads(datastring)
        except ValueError:
            msg = ("Cannot understand JSON")
            raise exception.MalformedRequestBody(reason=msg)
            
    def default(self, datastring):                                                                                                             
        return {'body': self._from_json(datastring)}

class DictSerializer(ActionDispatcher):                                                                                                        
    """Default request body serialization"""
    
    def serialize(self, data, action='default'):
        return self.dispatch(data, action=action)
    
    def default(self, data):  
        return ""

class JSONDictSerializer(DictSerializer):
    """Default JSON request body serialization"""

    def default(self, data):
        def sanitizer(obj):
            return unicode(obj)
        return jsonutils.dumps(data, default=sanitizer)
