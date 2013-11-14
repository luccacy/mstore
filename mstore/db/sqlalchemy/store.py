from mstore.db.sqlalchemy import api
from mstore.db.sqlalchemy import models
from mstore.common import exception
from mstore.common import logger
import time

LOG = logger.get_logger(__name__)

def store_to_db(batterys_id, sensor_n, sensor_id, user_id, values, status):
    
    try:
        print('================')
        print('batterys_id: %s' % batterys_id)
        print('sensor_n: %s' % sensor_n)
        print('sensor_id: %s' % sensor_id)
        print('user_id: %s' % user_id)
        
        print('================')
        elec = values['elec']
        if elec < 0:
            elec = None
            
        inners = values['inners']
        volts = values['volts']
        hinners = values['hinners'] 
        tempers = values['temps']
        
        '''get common values'''
        batterys_ref = api.batterys_get_by_id(batterys_id)
        base_id = int(batterys_ref.BASE_N)
        base_type_id = int(batterys_ref.BASE_TYPE)
        dict_battery_id = batterys_ref.BATTERYTYPE_V
        cur_batterytype_id = batterys_ref.BATTERYTYPE_V
        
        warning_ref = api.warning_get_by_id(base_type_id)
        dict_battery_ref = api.dictbattery_get_by_id(dict_battery_id)
        
        '''warning values'''
        yellow_max_red = warning_ref.YELTHRMAXRED_N
        yellow_max_yellow = warning_ref.YELTHRMAXYEL_N
        green_max_yellow = warning_ref.GRETHRMAXYEL_N
        green_max_red = warning_ref.GRETHRMAXRED_N
        
        '''standard values'''
        std_inner = dict_battery_ref.STDINNER_V
        std_inner_yellow = dict_battery_ref.YELLOWVALUE_N
        std_inner_red = dict_battery_ref.REDVALUE_N
        
        '''forcast factor'''
        b0 = dict_battery_ref.B0
        b1 = dict_battery_ref.B1
        
        timestamp = time.time()
        timestruct = time.localtime(timestamp)
        cur_date = time.strftime('%Y-%m-%d', timestruct)
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
        
        cur_base_id = base_id
        cur_batterys_id = batterys_id
        
        '''update battery table'''
        for bt_n in range(len(inners)):
            if inners[bt_n] < 0 :
                continue
            
            battery_serial_n = (sensor_n*8 + bt_n)
            cur_serial_n = battery_serial_n
            
            if status != 'failed':
                
                if len(tempers) > 0:
                    cur_temper = tempers[bt_n]
                else:
                    cur_temper = None
                cur_hinner = hinners[bt_n]               
                cur_inner = inners[bt_n]
                cur_volt = volts[bt_n]
                cur_forcast = float(b0) + float(b1)*float(cur_inner)
                
                if cur_inner <= std_inner_yellow:
                    cur_status = 0
                elif cur_inner <= std_inner_red:
                    cur_status = 1
                else:
                    cur_status = 2
            else:
                cur_temper = None
                cur_hinner = None
                cur_inner = None
                cur_volt = None
                cur_forcast = None
                cur_status = '采集数据失败'
            
            '''create pickdata'''
            pickdata_values = {'USER_ID' : user_id,
                               'BTKEY_V' : cur_batterys_id,
                               'BASENAME_V' : cur_base_id,
                               'SENSORNAME_V' : sensor_id,
                               'SENSOR_N' : sensor_n,
                               'BATTERY_N' : cur_serial_n,
                               'PICKEDTIME_D' : cur_time,
                               'VOL_N' : cur_volt,
                               'ELEC_N' : elec,
                               'INTER_N' : cur_inner,
                               'TEMPER_N' : cur_temper,
                               'HINTER' : cur_hinner,
                               'STATUS_V': cur_status,
                               }
            
            pickdata_ref = api.pickdata_create(pickdata_values)
            
            if status == 'failed':
                continue
        
            battery_values = {'BASE_N' : cur_base_id,
                          'GROUP_V' : cur_batterys_id,
                          'SERIAL_N' : cur_serial_n, 
                          'BATTERYTYPE_V' : cur_batterytype_id,
                          'CURDATE_D' : cur_time,
                          'STATUS_N' : cur_status,
                          'CURVAL_N' : cur_volt,
                          'CURINNER_N' : cur_inner,
                          'CUR_HL_INNER_N' : cur_hinner,
                          'CUR_TEMPERATURE_N' : cur_temper,
                          'FORCASTVOLUME_N' : cur_forcast,
                          }
            battery_ref = api.battery_get_by_groupid_and_serialnum(cur_batterys_id, cur_serial_n)
            if not battery_ref:
                battery_ref = api.battery_create(battery_values)
            else:
                api.battery_update(cur_batterys_id, cur_serial_n, battery_values)
                
            '''create btrundata'''
            btrundata_values = {'BTKEY_V' : cur_batterys_id,
                                'BASE_N' : cur_base_id,
                                'BTTYPEKEY_V' : cur_batterytype_id,
                                'RUNTIME_D': cur_time,
                                'STATUS_N' : cur_status,
                                'VOL_N' : cur_volt,
                                'INTER_N' : cur_inner,
                                'FORCASTVOLUME_N' : cur_forcast,
                                'CUR_HL_INNER_N' : cur_hinner,
                                'CUR_TEMPERATURE_N' : cur_temper,
                                'BTSERIALNO_V' : cur_serial_n,
                                }
            btrundata_ref = api.btrundata_create(btrundata_values)
            
            
            
        '''update batterys table'''
        sum_green = api.battery_get_count_by_status(cur_batterys_id,  0)
        sum_yellow = api.battery_get_count_by_status(cur_batterys_id,  1)
        sum_red = api.battery_get_count_by_status(cur_batterys_id,  2)
        
        if sum_red > yellow_max_red or sum_yellow > yellow_max_yellow or (sum_red+sum_yellow) > yellow_max_yellow:
            batterys_status = 2
        elif sum_yellow > green_max_yellow or sum_red > green_max_red or (sum_red+sum_yellow) > green_max_yellow:
            batterys_status = 1
        else:
            batterys_status = 0
        
        '''update batterys values'''
        batterys_values = {'RECORD_ID' : cur_batterys_id,
                           'GREEN' : sum_green,
                           'YELLOW' : sum_yellow,
                           'RED' : sum_red,
                           'STATUS_N' : batterys_status,
                           }
        
        api.batterys_update(cur_batterys_id, batterys_values)
        
        return
        
    except:
        batterys_ref = api.batterys_get_by_id(batterys_id)
        base_id = int(batterys_ref.BASE_N)
        timestamp = time.time()
        timestruct = time.localtime(timestamp)
        cur_date = time.strftime('%Y-%m-%d', timestruct)
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
        cur_serial_n = None
        elec = None
        cur_temper = None
        cur_hinner = None
        cur_inner = None
        cur_volt = None
        cur_forcast = None
        cur_status = '采集数据失败'
        
        pickdata_values = {'USER_ID' : user_id,
                            'BTKEY_V' : cur_batterys_id,
                            'BASENAME_V' : cur_base_id,
                            'SENSORNAME_V' : sensor_id,
                            'SENSOR_N' : sensor_n,
                            'BATTERY_N' : cur_serial_n,
                            'PICKEDTIME_D' : cur_time,
                            'VOL_N' : cur_volt,
                            'ELEC_N' : elec,
                            'INTER_N' : cur_inner,
                            'TEMPER_N' : cur_temper,
                            'HINTER' : cur_hinner,
                            'STATUS_V': cur_status,
                            }
            
        pickdata_ref = api.pickdata_create(pickdata_values)
        
        LOG.error('failed to pick sensor_id : %d data', sensor_id)
        return

    
def delete_records_over_one_week_day():
    
    try:
        timestamp = time.time() - 24*60*60*7
        timestruct = time.localtime(timestamp)
        one_day_before = time.strftime('%Y-%m-%d', timestruct)
        
        api.pickdata_delete_by_time(one_day_before)
    
    except:
        LOG.error('failed to delete record')
    

    
    
    
    
    
# volt =  [221,222,223,224,225,226,227,228,229,230]
# inner = [441,442,443,444,445,446,447,448,449,450]
#     
# '''get batterys by batterys_id'''
# batterys_id = '111111-1'
# batterys_ref = api.batterys_get_by_id(batterys_id)
# sum_green = 0
# sum_yellow = 0
# sum_red = 0
#  
# '''get warning thread values by batterys base type'''
# base_id = int(batterys_ref.BASE_TYPE)
# print('=========%s', base_id)
# warning_ref = api.warning_get_by_id(base_id)
# yellow_max_red = warning_ref.YELTHRMAXRED_N
# yellow_max_yellow = warning_ref.YELTHRMAXYEL_N
# green_max_yellow = warning_ref.GRETHRMAXYEL_N
# green_max_red = warning_ref.GRETHRMAXRED_N
#  
# '''get dict battery type'''
# dict_battery_id = batterys_ref.BATTERYTYPE_V
# dict_battery_ref = api.dictbattery_get_by_id(dict_battery_id)
# b0 = dict_battery_ref.B0
# b1 = dict_battery_ref.B1
# std_inner = dict_battery_ref.STDINNER_V
# std_inner_yellow = dict_battery_ref.YELLOWVALUE_N
# std_inner_red = dict_battery_ref.REDVALUE_N
#  
# '''BTKEY_V'''
# cur_batterys_id = batterys_id 
# '''BASE_N'''
# cur_base_id = batterys_ref.BASE_N
#  
# '''BATTERYTYPE_V'''
# cur_batterytype_id = batterys_ref.BATTERYTYPE_V
# '''RUNTIME_D'''
# timestamp = time.time()
# timestruct = time.localtime(timestamp)
# cur_date = time.strftime('%Y-%m-%d', timestruct)
# cur_time = time.strftime('%Y-%m-%d %H:%M:%S', timestruct)
# 
# for i in range(len(volt)):
#     '''BTSERIALNO_V'''
#     serial_num = i
#     '''STATUS_N'''
#     '''VOL_N'''
#     cur_volt = volt[i]/100.0
#     '''INTER_N'''
#     cur_inner = inner[i]/1000.0
#     '''CUR_ELECTRIC_N'''
#     '''CUR_HL_INNER_N'''
#     '''CUR_TEMPERATURE_N'''
#     '''FORCASTVOLUME_N'''
#     cur_forcast = float(b0) + float(b1)*float(cur_inner)
#     print('b0 : %f, b1 : %f' % (float(b0), float(b1)))
#     print('v : %f, i : %f, f : %f' % (cur_volt, cur_inner, cur_forcast))
#     '''update batterys red yellow and red status battery num
#        update batterys status'''
#      
#     if cur_inner <= std_inner_yellow:
#         cur_status = 0
#         sum_green = sum_green + 1
#     elif cur_inner <= std_inner_red:
#         cur_status = 1
#         sum_yellow = sum_yellow + 1
#     else:
#         cur_status = 2
#         sum_red = sum_red + 1
#          
#     if sum_red > yellow_max_red or sum_yellow > yellow_max_yellow or (sum_red+sum_yellow) > yellow_max_yellow:
#         batterys_status = 2
#     elif sum_yellow > green_max_yellow or sum_red > green_max_red or (sum_red+sum_yellow) > green_max_yellow:
#         batterys_status = 1
#     else:
#         batterys_status = 0
#      
#     '''create btrundata'''
#     btrundata_values = {'BTKEY_V' : cur_batterys_id,
#                         'BASE_N' : cur_base_id,
#                         'BTTYPEKEY_V' : cur_batterytype_id,
#                         'RUNTIME_D': cur_time,
#                         'STATUS_N' : cur_status,
#                         'VOL_N' : cur_volt,
#                         'INTER_N' : cur_inner,
#                         'FORCASTVOLUME_N' : cur_forcast,
#                         'BTSERIALNO_V' : serial_num,
#                         }
#     btrundata_ref = api.btrundata_create(btrundata_values)
#     
#     '''create pickdata'''
#     pickdata_values = {'USER_ID' : '',
#                        'BTKEY_V' : cur_batterys_id,
#                        'BASENAME_V' : cur_base_id,
#                        'SENSORNAME_V' : '',
#                        'SENSOR_N' : '',
#                        'BATTERY_N' : '',
#                        'PICKEDTIME_D' : cur_time,
#                        'VOL_N' : cur_volt,
#                        'ELEC_N' : '',
#                        'INTER_N' : cur_inner,
#                        'STATUS_V': cur_status,
#                        }
#     
#     pickdata_ref = api.pickdata_create(pickdata_values)
#      
#     '''update battery current inner, vol , forcast and so on
#        update battery data time
#        update battery status'''
#  
#     battery_values = {'BASE_N' : cur_base_id,
#                       'GROUP_V' : cur_batterys_id,
#                       'SERIAL_N' : serial_num, 
#                       'BATTERYTYPE_V' : cur_batterytype_id,
#                       'CURDATE_D' : cur_time,
#                       'STATUS_N' : cur_status,
#                       'CURVAL_N' : cur_volt,
#                       'CURINNER_N' : cur_inner,
#                       'FORCASTVOLUME_N' : cur_forcast,
#                       }
#      
#     battery_ref = api.battery_get_by_groupid_and_serialnum(cur_batterys_id, serial_num)
#     if not battery_ref:
#         battery_ref = api.battery_create(battery_values)
#     else:
#         api.battery_update(cur_batterys_id, serial_num, battery_values)
#         
#     '''update batterys values'''
#     batterys_values = {'RECORD_ID' : cur_batterys_id,
#                        'GREEN' : sum_green,
#                        'YELLOW' : sum_yellow,
#                        'RED' : sum_red,
#                        'STATUS_N' : batterys_status,
#                        }
#     
#     api.batterys_update(cur_batterys_id, batterys_values)