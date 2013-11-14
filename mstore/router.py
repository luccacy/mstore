import routes as routes_mapper
import attributes
import webob
import webob.dec
import webob.exc
import wsgi
import base

from mstore.common import logger

LOG = logger.get_logger(__name__)
RESOURCES = {'dhcp': 'dhcps',
             'kickstart': 'kickstarts',
             'pxe': 'pxes',
             'service': 'services',
             'deplylog': 'deploylogs',
             'deploy': 'deploys',
             'hostname' : 'hostnames',
             'firewall' : 'firewalls',
             'node' : 'nodes',
             'system': 'systems', 
             'interface':'interfaces',
             'task':'tasks'}
            
#SUB_RESOURCES = {}                                                                                                                           
COLLECTION_ACTIONS = ['index', 'create']
MEMBER_ACTIONS = ['show', 'update', 'delete']
#REQUIREMENTS = {'id': attributes.UUID_PATTERN, 'format': 'xml|json'}


class APIRouter(wsgi.Router):
    @classmethod
    def factory(cls, global_config, **local_config):    
                                                                      
        return cls(**local_config)

    def __init__(self, **local_config):

        mapper = routes_mapper.Mapper()
        col_kwargs = dict(collection_actions=COLLECTION_ACTIONS,                                                                     
                          member_actions=MEMBER_ACTIONS)
        def _map_resource(collection, resource, params, parent=None):
            allow_bulk = False 
            allow_pagination = None 
            allow_sorting = False 
            plugin = None
            controller = base.create_resource(
                collection, resource, plugin, params, allow_bulk=allow_bulk,
                parent=parent, allow_pagination=allow_pagination,
                allow_sorting=allow_sorting)
            path_prefix = None                    
            if parent:                            
                path_prefix = "/%s/{%s_id}/%s" % (parent['collection_name'],
                                                  parent['member_name'],
                                                  collection)
            mapper_kwargs = dict(controller=controller,
                                # requirements=REQUIREMENTS,
                                 path_prefix=path_prefix,
                                 **col_kwargs)

            return mapper.collection(collection, resource,
                                     **mapper_kwargs)
            
        #mapper.connect('index', '/', controller=Index(RESOURCES))
        for resource in RESOURCES:
            _map_resource(RESOURCES[resource], resource,
                          attributes.RESOURCE_ATTRIBUTE_MAP.get(
                              RESOURCES[resource], dict()))

        super(APIRouter, self).__init__(mapper)
