import telnetlib
import sys
import os

from mstore.common import cfg

core_opts = [
    cfg.StrOpt('port', default='8989',
                help=('The mstore server listen port')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)


def telnet(host):
    status = ''
    msg = ''
    try:
        tn = telnetlib.Telnet(host, port=CONF.port, timeout=3)
    except Exception:
        status = 'inactive'
        msg = 'connected timeout'
        return status,msg
    
    tn.close()
    status = 'active'
    msg = 'connected ok'
    return status,msg
