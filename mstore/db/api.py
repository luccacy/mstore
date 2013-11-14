'''
Created on 2013-9-1

@author: zhouyu
'''

from mstore.db.sqlalchemy import api
from mstore.db.sqlalchemy import store


IMPL = api

def sensor_get_all():
    return IMPL.sensor_get_all()

def sensor_get_by_id(sensor_id):
    return IMPL.sensor_get_by_id(sensor_id)

def cyclesetting_get_cycle(id=1):
    return IMPL.cyclesetting_get_cycle(id)

def store_to_db(batterys_id, sensor_n, sensor_id, user_id, values, status):
    return store.store_to_db(batterys_id, sensor_n, sensor_id, user_id, values, status)

def delete_records_over_one_week_day():
    return store.delete_records_over_one_week_day()