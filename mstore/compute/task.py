'''
Created on 2013-12-17

@author: zhouyu
'''
from mstore.compute import engine
from mstore.common import logger

LOG = logger.get_logger(__name__)

class TaskBase(object):
    def __init__(self):
        self._engine = engine.get_engine()
        
    def __call__(self):
        pass
    

class Rgb2grayTask(TaskBase):
    
    def __init__(self, src_img_path, dst_img_path):
        super(Rgb2grayTask, self).__init__()
        self._adapter = self._engine.get_adapter('rgb2gray')
        self.src_img_path = src_img_path
        self.dst_img_path = dst_img_path
    
    def __call__(self):
        try:
            self._adapter.run(self.src_img_path, self.dst_img_path)
        except:
            LOG.exception('failed to run rgb2gray task')
    
    def rollback(self):
        pass
