import os
import sys
import errno
from mstore.common import logger

LOG = logger.get_logger(__name__)

def write(file_name, file_context):

    try:
        with open(file_name, 'w') as fp:
            fp.write(file_context)
    except Exception, e:
        LOG.error('write file exception: %s', e)
        raise 'Failed to write file : %s' % file_name

def ensure_tree(path):
    """Create a directory (and any ancestor directories required)

    :param path: Directory to create
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            if not os.path.isdir(path):
                raise
        else:
            raise