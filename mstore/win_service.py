'''
Created on 2013-9-3

@author: zhouyu
'''
import win32serviceutil
import win32service
import win32event
from mstore import server
import time
import thread

class KnightService(win32serviceutil.ServiceFramework):
    
    _svc_name_ = "mstore service"
    _svc_display_name_ = "battery monitor service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # And set my event.
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        #self.timeout=5*1000 #sleep 5 seconds
        
        #while True:
            #time.sleep(1)
            #thr = Thread(server.main, name='mstore')
            #thr.start
        #server.main()
        thread.start_new(server.main, ())
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        #if win32event.WaitForSingleObject(self.hWaitStop, self.timeout) == win32event.WAIT_OBJECT_0:
                #break

#win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(KnightService) 