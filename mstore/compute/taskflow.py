'''
Created on 2013-12-17

@author: zhouyu
'''
from mstore.compute import utils
import uuid as uuidlib

class TaskFlow(object):
    
    def __init__(self, uuid=None):
        self.runners = []
        self.result = None
        if not uuid:
            self._id = str(uuidlib.uuid4())
        else:
            self._id = str(uuid)

    def uuid(self):
        return (self._id)

    def reset(self):
        self.result = None
    
    def add(self, task):
        r = utils.Runner(task)
        self.runners.append(r)
        
    def remove(self, task):
        pass
        
    def run(self, *args, **kwargs):
        for r in self.runners:
            r(*args, **kwargs)
            
    
    