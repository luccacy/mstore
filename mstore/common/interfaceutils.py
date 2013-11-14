import os
import sys

from mstore.common import processutils
from mstore.common import fileutils

DNS_CONF_FILE = '/etc/resolv.conf'

def _exec(*cmd, **kwargs):
    return processutils.execute(*cmd, **kwargs)

def _format_interface(device, ip, netmask, gw, nameserver):
    if device is None or ip is None:
        raise 'the device and ip is invalid'
    else:
        result = "DEVICE=%s\n" % device
        result += "TYPE=Ethernet\n"
        result += "ONBOOT=yes\n"
        result += "NM_CONTROLLED=yes\n"
        result += "BOOTPROTO=static\n"
        result += "IPADDR=%s\n" % ip

    if netmask is not None:
        result += 'NETMASK=%s\n' % netmask
    if gw is not None:
        result += 'GATEWAY=%s' % gw

    return result

def _get_net(ip, netmask):
    
    if ip is None or netmask is None:
        raise 'ip and netmask is invalid'

    _netmask = {'255.255.255.0':3,
                '255.255.0.0':2,
                '255.0.0.0':1}
    bit = _netmask[netmask]

    ip_list = ip.split('.')
    
    net = ''

    for i in range(bit):
        net += ip_list[i]
        net += '.'

    for i in range(4 - bit):
        net += '0'
        if i != (3-bit) :
            print i
            net += '.'

    return net

def set_interface(device, ip, netmask, gw, nameserver):
    CONF_FILE = ''

    if device is not None and ip is not None:
        CONF_FILE = '/etc/sysconfig/network-scripts/ifcfg-%s' % device
        _exec('ifconfig %s %s netmask %s' % (device, ip, netmask), shell=True)
    if gw is not None:
        net = _get_net(ip, netmask)
        _exec('route add -net %s gw %s dev %s' % (gw, net, device), shell=True)
    if nameserver is not None:
        _exec("echo 'nameserver %s' >> %s" % (nameserver, DNS_CONF_FILE), shell=True)

    if CONF_FILE is not None:
        if os.path.exists(CONF_FILE):
            _exec('rm -f %s' % CONF_FILE, shell=True)

        fcontext = _format_interface(device, ip, netmask, gw, nameserver)
        fileutils.write(CONF_FILE, fcontext)
