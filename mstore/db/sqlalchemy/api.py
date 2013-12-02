'''
Created on 2013-9-1

@author: zhouyu
'''
from mstore.db.sqlalchemy.session import get_session
from mstore.db.sqlalchemy import models
from mstore.common import exception
from mstore.common import logger

LOG = logger.get_logger(__name__)

def model_query(model, *args, **kwargs):
    """Query helper that accounts for context's `read_deleted` field.
    """
    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)

    return query

def account_create(values, session=None):
    account_ref = models.Account()
    
    account_ref.update(values)
    if session is None:
        session = get_session()
    account_ref.save(session=session)
    return account_ref

def account_get_by_id(id, session=None):
    if session is None:
        session = get_session()
    result = model_query(models.Account, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        LOG.error('failed to find sensor from sensor_id : %d', id)
        return None

    return result

def account_delete_by_id(id, session=None):
    if session is None:
        session = get_session()
        
    account_ref = model_query(models.Account, session=session).\
                    filter_by(id=id).\
                    first()
    
    session.delete(account_ref)
    session.flush()

def container_create(values, session=None):
    container_ref = models.Container()
    
    container_ref.update(values)
    if session is None:
        session = get_session()
    container_ref.save(session=session)
    return container_ref

def container_get_by_id(id, session=None):
    if session is None:
        session = get_session()
    result = model_query(models.Container, session=session).\
                     filter_by(id=id).\
                     first()
    if not result:
        LOG.error('failed to find sensor from sensor_id : %d', id)
        return None

    return result

def container_get_by_name(name, session=None):
    if session is None:
        session = get_session()
    result = model_query(models.Container, session=session).\
                     filter_by(name=name).\
                     first()
    if not result:
        LOG.error('failed to find sensor from sensor_id : %d', id)
        return None

    return result

def container_delete_by_name(name, session=None):
    if session is None:
        session = get_session()
        
    container_ref = model_query(models.Container, session=session).\
                    filter_by(id=id).\
                    first()
    
    session.delete(container_ref)
    session.flush()
    
def object_create(values, session=None):
    object_ref = models.Object()
    
    object_ref.update(values)
    if session is None:
        session = get_session()
    object_ref.save(session=session)
    return object_ref

def object_get_by_name(name, session=None):
    if session is None:
        session = get_session()
    result = model_query(models.Object, session=session).\
                     filter_by(name=name).\
                     first()
    if not result:
        LOG.error('failed to find sensor from sensor_id : %d', id)
        return None

    return result

def object_get_by_container_id(container_id, session=None):
    if session is None:
        session = get_session()
    results = model_query(models.Object, session=session).\
                     filter_by(container_id=container_id).\
                     all()
    if not results:
        return None
    
    return results

def object_delete_by_container_id(container_id, session=None):
    if session is None:
        session = get_session()
    results = model_query(models.Object, session=session).\
                     filter_by(container_id=container_id).\
                     first()
    if results:
        for result in results:
            session.delete(result)
            session.flush()
