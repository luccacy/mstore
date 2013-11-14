'''
Created on 2013-8-29

@author: zhouyu
'''
'''
import string, threading, time
 
def thread_main(a):
    global count, mutex

    threadname = threading.currentThread().getName()
 
    while True:
        print("%s, %s" % (threadname, a))
        time.sleep(1)
 
def main(num):

    threads = []


    threads.append(threading.Thread(target=thread_main, args=(1,)))
    threads.append(threading.Thread(target=thread_main, args=(2,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()  
        
    while True:
        print 'main thread'
        time.sleep(1)
 
 
if __name__ == '__main__':
    num = 4

    main(4)
'''

