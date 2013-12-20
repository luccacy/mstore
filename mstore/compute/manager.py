'''
Created on 2013-12-17

@author: zhouyu
'''
from mstore.compute import adpter
from mstore.compute import engine
from mstore.compute import taskflow
from mstore.compute import task
from mstore.common import importutils
from mstore.common import cfg
import sys

cfg.CONF(args=sys.argv[1:], project='mstore')
# 
adpter.load_all_adapters(adpter.__path__[0])
# 
# _engine = engine.get_engine()
# color_gray = _engine.get_adapter('color2gray')
# color_gray.run('/root/lena.jpg', '/root/love.jpg')

_task_flow = taskflow.TaskFlow()
_task = task.Rgb2grayTask('/root/lena.jpg', '/root/love.jpg')
_task_flow.add(_task)
_task_flow.run()

