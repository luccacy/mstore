'''
Created on 2013-9-18

@author: zhouyu
'''
from mstore.common import serialfake
from mstore.common import serialutils

class SerialAgent(object):
    
    def __init__(self, port):
        self._driver = serialfake.SerialControl(port)
        #self._driver = serialutils.SerialControl(port)
        self.output = self._driver.output
        
    def open(self):
        self._driver.open()
        
    def close(self):
        self._driver.close()

    def start_thread(self):
        self._driver.start_thread()

    def stop_thread(self):
        self._driver.stop_thread()
    
    def read_thread(self):
        self._driver.read_thread()
    
    def write(self, data):
        self._driver.write(data)
        self.output = self._driver.output