from mstore.common import logger

from eventlet import Timeout

LOG = logger.get_logger(__name__)

_FATAL_EXCEPTION_FORMAT_ERRORS = False

class BaseException(Exception):
    
    message = 'An unknown exception occurred'

    def __init__(self, **kwargs):
        
        try:
            self._error_string = self.message % kwargs

        except Exception as e:
            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise e
            else: 
                self._error_string = self.message

    def __str__(self):
        return self._error_string

class InvalidArgs(BaseException):
    message = 'Invalid input arguments'

class NotImplementedError(BaseException):
    message = 'Not implement interface'

class MalformedRequestBody(BaseException):
    message = 'Invalid fromed request'

class Duplicate(BaseException):
    message = 'duplicate database entry'
      
class SensorNotFound(BaseException):
    message = 'sensor not found'  
    
    
class ChunkReadTimeout(Timeout):
    pass


class ChunkWriteTimeout(Timeout):
    pass


class ConnectionTimeout(Timeout):
    pass
