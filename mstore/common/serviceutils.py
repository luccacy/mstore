import os
import sys

from mstore.common import processutils
from mstore.common import cfg

core_opts = [
    cfg.StrOpt('mount_dir', default='/var/ftp/centos',
                help=('The rock os mounted directory')),
    cfg.StrOpt('iso_file', default='/root/RockCloudOS.iso',
                help=('The rock os file path')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

service_conf_files = {'pxe': '/var/lib/tftpboot/pxelinux.0',
                      'kickstart' : '/var/ftp/ks.cfg',
                      'iso' : '/var/ftp/centos/isolinux'}

def _exec(*cmd, **kwargs):
    return processutils.execute(*cmd, **kwargs)

def get_service_status(ser_name):
    ret, err = _exec('service', ser_name, 'status')
    if ret.find('running') > 0:
        status = 'active'
    else:
        status = 'inactive'
    return status

def start_service(ser_name):
    ret,err = _exec('service', ser_name, 'restart')
    return get_service_status(ser_name)

def stop_service(ser_name):
    ret,err = _exec('service', ser_name, 'stop')
    return get_service_status(ser_name)

def check_all_services():
    stat = {'dhcpd':'', 'vsftpd': '', 'xinetd':'', 'tftp':'', 'pxe':'',
            'kickstart' : '', 'iso' :''}

    for ser in ('dhcpd', 'vsftpd', 'xinetd'):
        status = get_service_status(ser)
        stat[ser] = status         
    
    for ser in ('tftp',):
        ret, err = _exec('chkconfig', '--list', ser)
        if ret.find('on') > 0:
            status = 'active'
        else:
            _exec('chkconfig', 'tftp', 'on')
            start_service('vsftpd')
            start_service('xinetd')
            ret, err = _exec('chkconfig', '--list', ser)
            if ret.find('on') > 0:
                status = 'active'
            else:
                status = 'inactive'
        stat[ser] = status

    iso_file= CONF.iso_file
    mount_dir = CONF.mount_dir 
    
    if not os.path.exists(service_conf_files['iso']):
        if not os.path.exists(iso_file):
            stat['iso'] = 'inactive'
        else:
            _exec('mount -o loop %s %s' % (iso_file, mount_dir), shell=True)

    for ser in ('pxe', 'kickstart', 'iso'):
        if os.path.exists(service_conf_files[ser]):
            status = 'active'
        else:
            status = 'inactive'
        stat[ser] = status

    return stat

