'''
Created on 2013-12-17

@author: zhouyu
'''
from mstore.common import importutils
from mstore.compute import adpter

class EngineBase(object):
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            singleton = super(EngineBase, cls)
            cls._instance = singleton.__new__(cls, *args, **kwargs)
            
        return cls._instance
    

class ComputeEngine(EngineBase):

    algorithm_pool = {}
    
    def __init__(self):
        #adpter.load_all_adapters(adpter.__path__[0])
        pass
        
    def register(self, name, adapter):
        self.algorithm_pool[name] = adapter
        
    def unregister(self, name):
        self.algorithm_pool.pop(name)
    
    def get_adapter(self, name):
        return importutils.import_object(self.algorithm_pool[name])

def get_engine():
    engine =  ComputeEngine()
    return engine
    
