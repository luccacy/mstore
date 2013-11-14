import webob.dec
import webob.exc                                                                                                                     

import wsgi

def _query_to_dict(query):
    query_dict = {}
    if query == '':
        return 
    else:
        query_list = query.split('&')

        for item in query_list:
            k_v = item.split('=')
            v = k_v.pop()
            k = k_v.pop()
            query_dict[k] = v

    return query_dict

class Request(wsgi.Request):
    pass

def Resource(controller, faults=None, deserializers=None, serializers=None):
    deserializer = wsgi.JSONDeserializer()
    serializer = wsgi.JSONDictSerializer()

    @webob.dec.wsgify(RequestClass=Request)
    def resource(request):
        req_method = request.environ.get('REQUEST_METHOD')
        query = None 
        if req_method == 'GET': 
            query = request.environ.get('QUERY_STRING')

        route_args = request.environ.get('wsgiorg.routing_args')
        if route_args:
            args = route_args[1].copy()
        else:
            args = {}
        
        args.pop('controller', None)
        fmt = args.pop('format', None)
        action = args.pop('action', None)

        if request.body:
            args['body'] = deserializer.deserialize(request.body)['body']
        if query is not None:
            query_dict = _query_to_dict(query)
            args = dict(args, **query_dict)

        method = getattr(controller, action)
        result = method(request=request, **args) 

        body = serializer.serialize(result)
        return webob.Response(request=request, 
                              content_type='application/json',
                              body=body)
    return resource
