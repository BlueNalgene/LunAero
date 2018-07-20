#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

from __main__ import *
from Lconfig import USEGUI
from .Platform import platform_detect
#from .Manipulations import Manipulations

if USEGUI:
	from .Debuggui import Gui

if Platform.platform_detect() == 1:
	from .RasPiGPIO import RasPiGPIO
	from .MotorControl import MotorControl
