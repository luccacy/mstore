'''
Created on 2013-9-1

@author: zhouyu
'''
from sqlalchemy import Column, Integer, BigInteger, String, schema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship, backref, object_mapper

from mstore.db.sqlalchemy.session import get_session
from mstore.common import exception

BASE = declarative_base()

class DbBase(object):
    """Base class for Nova Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __table_initialized__ = False
    metadata = None

    def save(self, session=None):
        """Save this object."""
        if not session:
            session = get_session()
        session.add(self)
        try:
            session.flush()
        except IntegrityError, e:
            if str(e).endswith('is not unique'):
                raise exception.Duplicate()
            else:
                raise

    def delete(self, session=None):
        """Delete this object."""
        '''
        self.deleted = True
        self.deleted_at = timeutils.utcnow()
        '''
        self.save(session=session)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __iter__(self):
        columns = dict(object_mapper(self).columns).keys()
        # NOTE(russellb): Allow models to specify other keys that can be looked
        # up, beyond the actual db columns.  An example would be the 'name'
        # property for an Instance.
        if hasattr(self, '_extra_keys'):
            columns.extend(self._extra_keys())
        self._i = iter(columns)
        return self

    def next(self):
        n = self._i.next()
        return n, getattr(self, n)

    def update(self, values):
        """Make the model object behave like a dict"""
        for k, v in values.iteritems():
            setattr(self, k, v)

    def iteritems(self):
        """Make the model object behave like a dict.

        Includes attributes from joins."""
        local = dict(self)
        joined = dict([(k, v) for k, v in self.__dict__.iteritems()
                      if not k[0] == '_'])
        local.update(joined)
        return local.iteritems()
    
class Account(BASE, DbBase):
    
    __tablename__ = 'tbl_accounts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))
    telephone = Column(String(255))
    address = Column(String(255))
    company = Column(String(255))
    create_time = Column(DateTime)
    
class Container(BASE, DbBase):
    
    __tablename__ = 'tbl_containers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    account_id = Column(Integer)
    create_time = Column(DateTime)
    
class Object(BASE, DbBase):
    
    __tablename__ = 'tbl_objects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    container_id = Column(Integer)
    account_id = Column(Integer)
    create_time = Column(DateTime)
