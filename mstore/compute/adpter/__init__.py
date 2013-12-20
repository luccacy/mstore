import os
import imp
import mstore
import mstore.compute.adpter
from mstore.common import importutils
from mstore.common import logger
from mstore.common import cfg

core_opts = [
    cfg.StrOpt('lib_dir','/root/mstore/mstore/compute/adpter', 
                help=('The artisan server log directory')),
]

CONF = cfg.CONF
CONF.register_opts(core_opts)

LOG = logger.get_logger(__name__)

def load_all_adapters(path):

    for f in os.listdir(path):
        try:
            mod_name, file_ext = os.path.splitext(os.path.split(f)[-1])
            ext_path = os.path.join(path, f)

            if file_ext.lower() == '.py' and not mod_name.startswith('_'):
                mod = imp.load_source(mod_name, ext_path)
                reg = getattr(mod, 'register')
                reg()

        except Exception as exception:
            LOG.warn(("Extension file %(f)s wasn't loaded due to "
                        "%(exception)s"), {'f': f, 'exception': exception})
