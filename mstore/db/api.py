'''
Created on 2013-9-1

@author: zhouyu
'''

from mstore.db.sqlalchemy import api
from mstore.db.sqlalchemy import store


IMPL = api

def account_create(values, session=None):
    return IMPL.account_create(values, session)

def account_get_by_id(id, session=None):
    return IMPL.account_get_by_id(id, session)

def account_delete_by_id(id, session=None):
    return IMPL.account_delete_by_id(id, session)

def container_create(values, session=None):
    return IMPL.container_create(values, session)

def container_get_by_id(id, session=None):
    return IMPL.container_get_by_id(id, session)

def container_get_by_name(name, session=None):
    return IMPL.container_get_by_name(name, session)

def container_delete_by_name(name, session=None):
    return IMPL.container_delete_by_name(name, session)

def object_create(values, session=None):
    return IMPL.object_create(values, session)

def object_get_by_name(name, session=None):
    return IMPL.object_get_by_name(name, session)

def object_get_by_container_id(container_id, session=None):
    return IMPL.object_get_by_container_id(container_id, session)

def object_delete_by_container_id(container_id, session=None):
    return IMPL.object_delete_by_container_id(container_id, session)