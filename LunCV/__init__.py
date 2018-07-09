#!/bin/usr/python3 -B

from .RasPiGPIO import *
from .MotorControl import MotorControl
from .Platform import Platform
from .Manipulations import Manipulations
from __main__ import *
if USEGUI:
	from .Debuggui import Gui
