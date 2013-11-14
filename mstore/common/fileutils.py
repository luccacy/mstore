import os
import sys
from mstore.common import logger

LOG = logger.get_logger(__name__)

def write(file_name, file_context):

    try:
        with open(file_name, 'w') as fp:
            fp.write(file_context)
    except Exception, e:
        LOG.error('write file exception: %s', e)
        raise 'Failed to write file : %s' % file_name

