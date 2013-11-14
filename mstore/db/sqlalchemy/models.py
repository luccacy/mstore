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
    
class Sensor(BASE, DbBase):
    
    __tablename__ = 'tbl_sensors'
    
    RECORD_ID = Column(Integer, primary_key=True)
    SENSORNAME_V = Column(String(255))
    GROUPNAME_V = Column(String(255))
    BASENAME_V = Column(String(255))
    PROVINCENAME_V = Column(String(255))
    CITYNAME_V = Column(String(255))
    COUNTRYNAME_V = Column(String(255))
    SENSOR_SETUP_NAME_V = Column(String(255))
    SENSOR_N = Column(Integer)
    BATTERYNUM_N = Column(Integer)
    SENSOR_ADDR_N = Column(Integer)
    COM_N = Column(Integer)
    IP_V = Column(String(255))
    SETUP_D = Column(DateTime)
    REMARK_V = Column(String(255))
    
class Pickdata(BASE, DbBase):
    
    __tablename__ = 'tbl_pickdata'
    
    RECORD_ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, primary_key=True)
    BTKEY_V = Column(String(255))
    BASENAME_V = Column(String(255))
    SENSORNAME_V = Column(String(255))
    SENSOR_SETUP_NAME_V = Column(String(255))
    SENSOR_N = Column(Integer)
    BATTERY_N = Column(Integer)
    PICKEDTIME_D = Column(DateTime)
    VOL_N = Column(Float)
    ELEC_N = Column(Float)
    INTER_N = Column(Float)
    HINTER_N = Column(Float)
    TEMPER_N = Column(Float)
    STATUS_V = Column(String(255))
    REMARK_V = Column(String(255))
    
class Warning(BASE, DbBase):
    
    __tablename__ = 'mtsys_basetype'
    
    RECORD_ID = Column(Integer, primary_key=True)
    BASE_TYPE = Column(String(255))
    YELTHRMAXRED_N = Column(Integer)
    YELTHRMAXYEL_N = Column(Integer)
    GRETHRMAXRED_N = Column(Integer)
    GRETHRMAXYEL_N = Column(Integer)
    REMARK = Column(String(255))
    CREATE_DATE = Column(DateTime)
    
class Battery(BASE, DbBase):
    
    __tablename__ = 'bt_battery'
    
    RECORD_ID = Column(Integer, primary_key=True)
    BASE_N = Column(Integer)
    GROUP_V = Column(String(255))
    SERIAL_N = Column(Integer)
    BATTERYTYPE_V = Column(Integer)
    CURDATE_D = Column(DateTime)
    STATUS_N = Column(Integer)
    CURVAL_N = Column(Float)
    CURINNER_N = Column(Float)
    CUR_ELECTRIC_N = Column(Float)
    CUR_HL_INNER_N = Column(Float)
    CUR_TEMPERATURE_N = Column(Integer)
    FORCASTVOLUME_N = Column(Float)
    TESTVOLUME_N = Column(Float)
    POWERSUPPLY_N = Column(Float)
    BACKLOAD_N = Column(Float)
    REMARK_V = Column(String(255))
    
class Batterys(BASE, DbBase):
    
    __tablename__ = 'bt_batterys'
    
    RECORD_ID = Column(String(255), primary_key=True)
    BASE_TYPE = Column(Integer)
    BASE_N = Column(Integer)
    GROUPNAME_V = Column(String(255))
    BATTERYTYPE_V = Column(Integer)
    BATTERYNUM_N = Column(Integer)
    SETUP_D = Column(DateTime)
    CUR_DATE = Column(DateTime)
    DEVICE_V = Column(String(255))
    IP_V = Column(String(255))
    PORT_N = Column(Integer)
    ADDR_N = Column(Integer)
    STATUS_N = Column(Integer)
    GREEN = Column(Integer)
    YELLOW = Column(Integer)
    RED = Column(Integer)
    MANCODE_V = Column(Integer)
    
class Btrundata(BASE, DbBase):
    
    __tablename__ = 'bt_rundata'
    
    RECORD_ID = Column(Integer, primary_key=True)
    BTKEY_V = Column(String(255))
    BASE_N = Column(Integer)
    BTSERIALNO_V = Column(String(255))
    '''for test'''
    BTTYPEKEY_N = Column(Integer)
    RUNTIME_D = Column(DateTime)
    STATUS_N = Column(Integer)
    VOL_N = Column(Float)
    INTER_N = Column(Float)
    CUR_ELECTRIC_N = Column(Float)
    CUR_HL_INNER_N = Column(Float)
    CUR_TEMPERATURE_N = Column(Integer)
    FORCASTVOLUME_N = Column(Float)

class Dictbattery(BASE, DbBase):
    
    __tablename__ = 'dict_battery'
    
    RECORD_ID = Column(Integer, primary_key=True)
    B0 = Column(String(128))
    B1 = Column(String(128))
    STDINNER_V = Column(String(128))
    YELLOWVALUE_N = Column(Float)
    REDVALUE_N = Column(Float)
    
class CycleSetting(BASE, DbBase):
    
    __tablename__ = 'tbl_setting'
    
    RECORD_ID = Column(Integer, primary_key=True)
    CYCLE_N = Column(Integer)
    
    
    
    
        
    
    