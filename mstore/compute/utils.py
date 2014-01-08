'''
Created on 2013-12-17

@author: zhouyu
'''
import os
import uuid as uuidlib
from ctypes import cdll

class Runner(object):
    """A helper class that wraps a task and can find the needed inputs for
    the task to run, as well as providing a uuid and other useful functionality
    for users of the task.

    TODO(harlowja): replace with the task details object or a subclass of
    that???
    """

    def __init__(self, task, uuid=None):
        
        self.task = task
        self.result = None
        if not uuid:
            self._id = str(uuidlib.uuid4())
        else:
            self._id = str(uuid)

    def uuid(self):
        return (self._id)

    def reset(self):
        self.result = None

    def __call__(self, *args, **kwargs):
        
        self.result = self.task(*args, **kwargs)
        return self.result
        
def load_library(path):
    lib = None
    if os.path.exists(path):
        lib = cdll.LoadLibrary(path)
        
    return lib
