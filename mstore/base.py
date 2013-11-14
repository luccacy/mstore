import resource as wsgi_resource

import subprocess
import commands 
#import deploy_agent
#import task_agent

class Controller(object):
    LIST = 'list'
    SHOW = 'show'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'

    def __init__(self, plugin, collection, resource, attr_info,                                                                      
                 allow_bulk=False, member_actions=None, parent=None,
                 allow_pagination=False, allow_sorting=False):
        if member_actions is None:
            member_actions = []
        #self._agent = deploy_agent.DeployAgent()
        self._agent = task_agent.TaskAgent()
        self._collection = collection.replace('-', '_')
        self._resource = resource.replace('-', '_')

    def index(self, request, **kwargs):
        method = getattr(self._agent, "list_%s" % self._collection)
        return method()
        

    def create(self, request, body=None, **kwargs):

        method = getattr(self._agent, "create_%s" % self._resource)
        args = body[self._collection]
        return method(args)

    def delete(self, request, id, **kwargs):
        method = getattr(self._agent, "delete_%s" % self._resource)
        return method(id)

    def update(self, request, id, body=None, **kwargs):
        method = getattr(self._agent, "update_%s" % self._resource)
        args = body[self._collection]
        return method(id, args)
        

    def show(self, request, id, **kwargs):
        method = getattr(self._agent, "get_%s" % self._resource)
        return method(id, **kwargs)

def create_resource(collection, resource, plugin, params, allow_bulk=False,
                    member_actions=None, parent=None, allow_pagination=False,
                    allow_sorting=False):
    controller = Controller(plugin, collection, resource, params, allow_bulk,
                            member_actions=member_actions, parent=parent,
                            allow_pagination=allow_pagination,
                            allow_sorting=allow_sorting)

    return wsgi_resource.Resource(controller)
