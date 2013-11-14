import os
import sys
from mstore.common import processutils
from mstore.common import logger

LOG=logger.get_logger(__name__)

def _exec(*cmd, **kwargs):
    return processutils.execute(*cmd, **kwargs)

def add_host(ip, hostname):
    try:
        cmd = "awk '/%s/{print NR}' /etc/hosts" % ip
        ret = _exec(cmd, shell=True)
        ip_n = ret[0][:-1]
        cmd = "awk '/%s/{print NR}' /etc/hosts" % hostname
        ret = _exec(cmd, shell=True)
        host_n = ret[0][:-1]

        if len(ip_n) == 0 and len(host_n) == 0:
            cmd = "echo '%s %s' >> /etc/hosts " % (ip, hostname)
            _exec(cmd, shell=True)
        elif len(ip_n) != 0 and len(host_n) == 0:
            cmd = "sed -i '%ss/.*/%s %s/g' /etc/hosts" % (ip_n, ip, hostname)
            _exec(cmd, shell=True)
        elif len(ip_n) == 0 and len(host_n) != 0:
            cmd = "sed -i '%ss/.*/%s %s/g' /etc/hosts" % (host_n, ip, hostname)
            _exec(cmd, shell=True)
        else:
            LOG.error('Invalid hostname and ip : %s, %s', hostname, ip)
    except Exception:
        raise

def restart():
    try:
        cmd = "ps ax|grep dnsmasq|grep -v grep |grep -v dhcp | awk '{print $1}'"
        ret = _exec(cmd, shell=True)
        pid = ret[0].split('\n')[0]

        cmd = "ps ax|grep dnsmasq|grep -v grep | grep -v dhcp | awk '{print $7}'"
        ret = _exec(cmd, shell=True)
        option = ret[0][:-1]

        if pid > '0':
            cmd = 'kill -9 %s' % (pid)
            _exec(cmd, shell=True)
        if option.find('listen') >= 0:
            cmd = 'dnsmasq --bind-interfaces %s' % option
            _exec(cmd, shell=True) 
    except Exception:
        raise

