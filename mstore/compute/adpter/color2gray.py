'''
Created on 2013-12-17

@author: zhouyu
'''
from ctypes import *
import os
import mstore
from mstore.compute import utils
from mstore.compute.engine import get_engine
from mstore.common import cfg



CONF = cfg.CONF

class ColorGray(object):
    
    def __init__(self):
        self.name = 'color2gray'
        self.lib_name = 'libcolor2gray.so'
        self.lib_path = os.path.join('/root/mstore/mstore/compute/adpter',self.lib_name)
        self.lib = self._load() 

    def _load(self):
        if os.path.exists(self.lib_path):
            return utils.load_library(self.lib_path)
    
    def run(self, src_image_path, dest_image_path):
        return self.lib.color2gray((c_char_p)(src_image_path),(c_char_p)(dest_image_path))
  
def register():
    engine = get_engine()
    engine.register('color2gray', 'mstore.compute.adpter.color2gray.ColorGray')
