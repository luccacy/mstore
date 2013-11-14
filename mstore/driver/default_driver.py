import os
import sys
from mstore.deploy_base import DeployBase
from mstore.client import client
from mstore import wsgi
from mstore.common import ping
from mstore.common import telnet 

from mstore.common import cfg
from mstore.common import logger 
from mstore.common import fileutils
from mstore.common import http 
from mstore.common import processutils
from mstore.common import serviceutils 
from mstore.common import dhcputils 
from mstore.common import interfaceutils 
from mstore.common import hostutils 
from mstore.common import exception
from mstore.common import dnsmasq 

from webob.exc import (HTTPError,
                       HTTPNotFound,
                       HTTPConflict,
                       HTTPBadRequest,
                       HTTPForbidden,
                       HTTPRequestEntityTooLarge,
                       HTTPInternalServerError,
                       HTTPServiceUnavailable)

template_dhcp = {'dhcp-server' : '', 'subnet' : '', 'netmask' : '255.255.255.0',
        'ip-start':'', 'ip-end':'', 'router': '', 
        'default-lease-time' : '600', 'max-lease-time' : '1200' }

template_pxe = {'ftp-server' : '', 'ks-device':'eth0'}
template_ks = {'ftp-server': '', 'root-passwd':'123456',
        'net-device':'eth0', 'net-bootproto':'', 'ip':'', 'netmask':'255.255.255.0',
        'gateway':'', 'nameserver':'8.8.8.8', 'hostname':'','hard-disk':'', 'boot-size':'200',
        'swap-size':'4096','root-size':'1','fstype':'ext4'}

template_deploy = {'reinit' : '', 'roler' : '', 'passwd' : '123456',
        'controller_hostname' : '', 'controller_ip': '', 'controller_ext_ip':
        '', 'hostname' : '','node_port':'eth0',  'node_ip': '', 'net_mode' : '', 'plugin' : '',
        'mode': '', 'int_port' : 'eth1', 'ext_port' : 'eth6'}

template_interface = {'device':'', 'ip':'', 'netmask':'255.255.255.0',
        'gateway':None, 'nameserver':None}

core_opts = [
    cfg.StrOpt('dhcp_conf_file', default='/etc/dhcp/dhcpd.conf',
                help=('The dhcpd config file path')),
    cfg.StrOpt('pxe_conf_file', default='/var/lib/tftpboot/pxelinux.cfg/default',
                help=('The pxe config file path')),
    cfg.StrOpt('ks_conf_file', default='/var/ftp/ks.cfg',
                help=('The kickstart config file path')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

LOG = logger.get_logger(__name__)

LOCALHOST = '127.0.0.1'
LOCALHOST_ID = '127-0-0-1'

class DefaultDriver(DeployBase):

    def __init__(self):
        self._dhcp_cache = template_dhcp
        self._pxe_cache = template_pxe 
        self._ks_cache = template_ks
        self._deploy_cache = template_deploy
        self._client = client.HTTPClient()
        self._interface_cache = template_interface

    def _format_dhcp(self):
        result = 'next-server %s;\n' % self._dhcp_cache['dhcp-server']
        result += 'filename "pxelinux.0";\n\n'
        result += 'subnet %s netmask %s {\n' % (self._dhcp_cache['subnet'],self._dhcp_cache['netmask'])
        result += '\trange dynamic-bootp %s %s;\n' % (self._dhcp_cache['ip-start'], self._dhcp_cache['ip-end'])
        result += '\toption routers %s;\n' % self._dhcp_cache['router']
        result += '\tdefault-lease-time %s;\n' % self._dhcp_cache['default-lease-time']
        result += '\tmax-lease-time %s;\n' % self._dhcp_cache['max-lease-time']
        result += '}'

        return result

    def _format_pxe(self):
        result = 'default vesamenu.c32\n'
        result += 'timeout 1\n\n'
        result += 'label linux\n'
        result += '\tmenu default\n'
        result += '\tkernel vmlinuz\n'
        result += '\tappend initrd=initrd.img ks=ftp://%s/ks.cfg ksdevice=%s' % (self._pxe_cache['ftp-server'], self._pxe_cache['ks-device'])

        return result

    def _format_ks(self):
        result = 'install\n'
        result += 'text\n'
        result += 'url --url ftp://%s/centos\n' % self._ks_cache['ftp-server']
        result += 'lang en_US.UTF-8\n'
        result += 'keyboard us\n'

        if self._ks_cache['net-bootproto'] == 'dhcp':            
            result += 'network --device %s --bootproto dhcp\n' % \
            (self._ks_cache['net-device'])

        elif self._ks_cache['net-bootproto'] == 'static':
            result += 'network --device %s --bootproto static --ip %s --netmask %s --gateway %s --nameserver %s --hostname %s \n' % \
            (self._ks_cache['net-device'], self._ks_cache['ip'],
                    self._ks_cache['netmask'], self._ks_cache['gateway'],
                    self._ks_cache['nameserver'], self._ks_cache['hostname'])
        else:
            raise exception.InvalidArgs() 
            
        result += 'rootpw %s\n' % self._ks_cache['root-passwd']
        result += 'timezone Asia/Shanghai\n'
        result += 'bootloader --location=mbr --append="quiet"\n'
        result += 'clearpart --all --initlabel\n'

        result += 'part /boot --fstype %s --size=%s\n' % \
        (self._ks_cache['fstype'], self._ks_cache['boot-size'])

        result += 'part swap --size=%s\n' % self._ks_cache['swap-size']
        result += 'part / --fstype %s --grow --size=%s\n' % \
        (self._ks_cache['fstype'], self._ks_cache['root-size'])

        result += 'selinux --disabled\n'
        result += 'firewall --disabled\n'
        result += 'reboot\n'
        result += '%packages\n'
        result += '@Core\n'
        result += '@server-policy\n'
        result += '%end\n'
        result += '%post\n'
        result += 'service iptables stop\n'
        result += 'chkconfig iptables off\n'
        result += 'chkconfig tftp on\n'
        result += '%end\n'

        return result

    def _format_deploy_cmd(self):
        
        cmd = ['openstack-deploy']
        for (k, v) in self._deploy_cache.items():
            if self._deploy_cache[k] and k != 'node_ip': 
                cmd.append('--%s' % k)
                cmd.append('%s' % self._deploy_cache[k])

        return tuple(cmd) 
   
    def _check_net_device(self):

        net_device_dir = '/sys/class/net/'
        status = 0
        msg = 'ok'

        for k in ('node_port', 'int_port', 'ext_port'):
            net_device_file = os.path.join(net_device_dir, self._deploy_cache[k])
            if not os.path.exists(net_device_file):
                status = 1
                msg = 'device %s dose not exists' % self._deploy_cache[k]

        return status, msg
                
    def _exec(self, *cmd, **kwargs):
        return processutils.execute(*cmd, **kwargs)
        
    def _ping(self, node):
        return ping.verbose_ping(node)
        
    def _telnet(self, node):
        return telnet.telnet(node)

    def create_dhcp(self, args):
        dhcpd_conf_file = CONF.dhcp_conf_file

        for(k, v) in args.items():
            self._dhcp_cache[k] = v

        LOG.debug("dhcp_cache : %s" % self._dhcp_cache)

        try:
            fcontext = self._format_dhcp()
            fileutils.write(dhcpd_conf_file, fcontext)
        except Exception:
            raise

    def get_dhcp(self, id):
        return {"dhcp" : self._dhcp_cache} 

    def update_dhcp(self, id, args):
        return self.create_dhcp(args)
        
    def create_kickstart(self, args):
        ks_conf_file = CONF.ks_conf_file

        for(k, v) in args.items():
            self._ks_cache[k] = v

        LOG.debug("ks_cache : %s" % self._ks_cache)

        try:
            fcontext = self._format_ks()
            fileutils.write(ks_conf_file, fcontext)
        except Exception:
            raise

    def get_kickstart(self, id):
        return {"kickstart" : self._ks_cache}
        
    def update_kickstart(self, id, args):
        return self.create_kickstart(args)

    def create_pxe(self, args):
        pxe_conf_file = CONF.pxe_conf_file

        for(k, v) in args.items():
            self._pxe_cache[k] = v

        LOG.debug("pxe_cache : %s" % self._pxe_cache)
        
        try:
            fcontext = self._format_pxe()
            fileutils.write(pxe_conf_file, fcontext)
        except Exception:
            raise

    def get_pxe(self, id):
        return {"pxe" : self._pxe_cache}

    def update_pxe(self, id, args):
        return self.create_pxe(args)

    def get_service(self, id, name):
        node = id.replace('-', '.')
        ser_name = name

        if node == LOCALHOST:
            try:
                status = serviceutils.get_service_status(ser_name)
                return {"service" : ser_name, "status" : status}
            except Exception:
                raise
        return http.scheduler(node, '/services/%s&%s' % (LOCALHOST_ID, 
            ser_name), method = 'GET')
        
    def create_service(self, args):
        node = args['node-ip']
        ser_name = args['name']
        if node == LOCALHOST:
            try:
                status = serviceutils.start_service(ser_name)
                return {"service" : ser_name, "status" : status}
            except Exception:
                raise

        args['node-ip'] = LOCALHOST
        body = {"services" : args}
        return http.scheduler(node, '/services', body=body, method = 'POST')

    def update_service(self, id, args):
        #use update to stop service
        node = args['node-ip']
        ser_name = id
        if node == LOCALHOST:
            try:
                status = serviceutils.stop_service(ser_name)
                return {"service" : ser_name, "status" : status}
            except Exception:
                raise
        args['node-ip'] = LOCALHOST
        body = {"services" : args}
        return http.scheduler(node, '/services/%s' % ser_name, body=body, method = 'PUT')
    
    def create_deploy(self, args):
        for (k, v) in args.items():
            self._deploy_cache[k] = v

        node = self._deploy_cache['node_ip']
        if node == LOCALHOST:
            try:
                stat, msg = self._check_net_device()
                if stat == 1:
                    return {"status": "error", "message": msg}
                cmd = self._format_deploy_cmd()
                (ret,errcode) = self._exec(*cmd)
                if ret.find('Congratulation') >= 0:
                    msg = "openstack deploy successfully"
                    return {"status":"ok", "message" : msg, "code" : "0"}
                else:
                    return {"status":"error", "message": ret, "code" : errcode}
            except Exception:
                raise

        args['node_ip'] = LOCALHOST 
        body = {'deploys' : args}
        return http.scheduler(node, '/deploys', body=body, method = 'POST')        
    
    def get_hostname(self, id):
        node = id.replace('-', '.')
        LOG.info('get hostname')
        
        if node == 'all':
            return hostutils.get_hosts()
            
        if node == LOCALHOST:
            try:
                cmd = 'hostname'
                ret,err = self._exec(cmd)
                return {"hostname" : ret[:-1]}
            except Exception:
                raise
        
        return http.scheduler(node, '/hostnames/%s' % LOCALHOST_ID, method = 'GET')

    def create_hostname(self, args):
        node = args['node-ip']
        hostname = args['hostname']

        if node == LOCALHOST:
            try:
                cmd = "sed -i 's/HOSTNAME=.*$/HOSTNAME=%s/g' /etc/sysconfig/network" % hostname
                ret,err = self._exec(cmd, shell=True)
                return{"status" : 'ok'}
            except Exception:
                raise
       
        args['node-ip'] = LOCALHOST
        body = {"hostnames" : args}
        return http.scheduler(node, '/hostnames', body=body, method='POST')

    def update_hostname(self, id, args):
        
        node = id.replace('-', '.')

        if node == LOCALHOST:
            ip = args['ip']
            hostname = args['hostname']
            
            try:
                dnsmasq.add_host(ip, hostname)
                dnsmasq.restart()
                return {'status':'ok'}
            except Exception:
                raise

        body = {'hostnames' : args}
        return http.scheduler(node, '/hostnames/%s' % LOCALHOST_ID, body = body, method = 'PUT')

    def get_firewall(self, id):
        node = id.replace('-', '.')
    
        if node == LOCALHOST:
            cmd = 'getenforce'
            ret,err = self._exec(cmd)
            
            if ret == 'Disabled':
                return {"status" : "disabled"}
            else:
                return {"status" : "enabled"}

        return http.scheduler(node, 'firewalls/%s' % LOCALHOST_ID, method = 'GET')

    def create_firewall(self, args):

        node = args['node-ip']
        status = args['status']

        if node == LOCALHOST:
            if status == 'disabled':
                cmd = "sed -i 's/^SELINUX=.*$/SELINUX=disabled/g' /etc/selinux/config" 
            else:
                cmd = "sed -i 's/^SELINUX=.*$/SELINUX=enforcing/g' /etc/selinux/config"

            ret,err = self._exec(cmd, shell=True)

            return {"status" : ret}
        
        args['node-ip'] = LOCALHOST
        resp,body = self._send(url, ext_url, method='POST', body=body)

        return http.scheduler(node, '/firewalls', body = body, method = 'POST')

    def get_node(self, id):

        if id == 'all':
            return dhcputils.get_dhcpd_ips()

        else:
            try:
                node = id.replace('-', '.')
                status, msg = self._telnet(node)
            except Exception:
                raise

        return {"node" : node, "status" : status, "message" : msg}
        
    def update_node(self, id, args):

        node = id.replace('-', '.')
        
        if node == LOCALHOST:
            cmd = 'reboot'
            ret,err = self._exec(cmd)

            return {"status": ret}

        args['node-ip'] = LOCALHOST
        body = {'nodes' : args}

        return http.scheduler(node, '/nodes', body = body, method = 'PUT')

    def get_system(self, id):

        ser_name = id

        if ser_name == 'all':
            status = serviceutils.check_all_services()
        else:
            raise exception.InvalidArgs() 

        return status 

    def create_interface(self, args):

        for(k, v) in args.items():
            self._interface_cache[k] = v

        node = args['node-ip']

        if node == LOCALHOST:
            try:
                device = self._interface_cache['device']
                ip = self._interface_cache['ip']
                netmask = self._interface_cache['netmask']
                gw = self._interface_cache['gateway']
                nameserver = self._interface_cache['nameserver']
    
                interfaceutils.set_interface(device, ip, netmask, gw, nameserver)
    
                return {'status':'ok'}
            except Exception:
                raise

        args['node-ip'] = LOCALHOST
        body = {'interfaces': args}
        return http.scheduler(node, '/interfaces', body=body, method='POST')

