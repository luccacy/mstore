from mstore.client import client as http
import cfg
import logger

CONF = cfg.CONF
LOG = logger.get_logger('scheduler')

LOCALHOST='127.0.0.1'

def scheduler(node, url, body=None, method=None):
    
    client = http.HTTPClient()
    dest_service = 'http://%s:%s' % (node, CONF.port)
    client.set_management_url(dest_service)

    if method == 'POST':
        resp,body = client.post(url, body=body)
    elif method == 'PUT':
        resp,body = client.put(url, body=body)
    elif method == 'GET':
        resp,body = client.get(url)
    elif method == 'DELETE':
        resp,body = client.delete(url)
    else:
        LOG.error('Not supported http method : %s', method)
        return

    return body

