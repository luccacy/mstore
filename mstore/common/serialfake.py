'''
Created on 2013-9-18

@author: zhouyu
'''
import serial
import threading
import time


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
        pass
        
    def close(self):
        pass

    def start_thread(self):
        pass

    def stop_thread(self):
        pass
    
    def read_thread(self):
        return self.output

    
    def write(self, data):
        try:
            
            cmd_code = int(hex(ord(data[4])),16)
            
            if cmd_code == 0x31:
                '''sample1'''
                self.output = '!' + data[1:]
            elif cmd_code == 0x32:
                '''sample2'''
                self.output = '!' + data[1:]
            elif cmd_code == 0x33:
                '''transport'''
                self.output = '!03xxxx3B383AB23B113B5E3B383B\
11xxxxxxxx0F440F570F390F3F0F\
530F57xxxxxxxx003AD83AC53B4B\
3AEB3A8C3Axxxxxxxx27\t\n'
            elif cmd_code == 0x34:
                '''ext_life'''
                self.output = '!' + data[1:]
            
            print 'fake output: %s' % self.output
            
        except serial.SerialException, e:
            raise
        