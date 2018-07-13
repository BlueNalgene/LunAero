#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

from __main__ import *
from Lconfig import USEGUI
from .RasPiGPIO import RasPiGPIO
from .MotorControl import MotorControl
from .Platform import platform_detect
from .Manipulations import Manipulations

if USEGUI:
	from .Debuggui import Gui
