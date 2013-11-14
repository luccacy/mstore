'''
Created on 2013-8-28

@author: zhouyu
'''
import serial
import threading
import time
from mstore.common import logger

LOG = logger.get_logger(__name__)

class SerialControl(object):
    
    def __init__(self, port):
        self.s = serial.Serial()
        self.s.port = port
        self.s.baudrate = 9600
        self.s.parity = serial.PARITY_NONE
        self.s.stopbits = serial.STOPBITS_ONE
        self.s.bytesize = serial.EIGHTBITS
        self.thread = None
        self.alive = threading.Event()
        self.output = ''
        
    def open(self):
        try:
            self.s.open()
            return True
        except serial.SerialException, e:
            LOG.error('failed to open serial')
            return False
        
    def close(self):
        #self.stop_thread()               #stop reader thread
        self.s.close()             #cleanup
        self.Destroy()                  #close windows, exit app

    def start_thread(self):
        """Start the receiver thread"""        
        self.thread = threading.Thread(target=self.read_thread)
        self.thread.setDaemon(1)
        self.alive.set()
        self.thread.start()

    def stop_thread(self):
        """Stop the receiver thread, wait util it's finished."""
        if self.thread is not None:
            self.alive.clear()          #clear alive event for thread
            self.thread.join()          #wait until thread has finished
            self.thread = None
    
    def read_thread(self):
        """Thread that handles the incomming traffic. Does the basic input
           transformation (newlines) and generates an SerialRxEvent"""
        while self.alive.isSet():               #loop while alive event is true
            try:
                text = self.s.read(1)          #read one, with timout
                if text:                            #check if not timeout
                    n = self.s.inWaiting()     #look if there is more to read
                    if n:
                        text = text + self.s.read(n) #get it
                
                self.output = self.output + text

            except serial.SerialException, e:
                LOG.error('failed to read serial data')
                self.output = None
                return
    
    def write(self, data):
        try:
            self.s.write(data)
            return True
        except serial.SerialException, e:
            LOG.error('failed to write serial data : %s', data)
            return False
        
if __name__ == '__main__':
    s = SerialControl(5)
    s.open()
    s.start_thread()
    s.write("#R#")
    time.sleep(1)
    print s.output
    
        



