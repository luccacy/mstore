from ctypes import *
import os

libcolor = cdll.LoadLibrary(os.getcwd() + '/libcolor2gray.so')
libcolor.color2gray((c_char_p)('/root/lena.jpg'), (c_char_p)('/root/gray.jpg'))
