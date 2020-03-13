# -*- coding: utf-8 -*-
import time

from myro import *

init("COM5")

forward(1, 1)
backward(1, 1)
turnLeft(1, 1)
turnRight(1, 1)
motors(1, 1)
time.sleep(1)
stop()
motors(-1, -1)
time.sleep(1)
stop()
