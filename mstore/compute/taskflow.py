'''
Created on 2013-12-17

@author: zhouyu
'''
from mstore.compute import utils

class TaskFlow(object):
    
    def __init__(self):
        self.runners = []
    
    def add(self, task):
        r = utils.Runner(task)
        self.runners.append(r)
        
    def remove(self, task):
        pass
        
    def run(self, *args, **kwargs):
        for r in self.runners:
            r(*args, **kwargs)
            
    
    