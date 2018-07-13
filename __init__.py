#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Contains the variables for:
-USEGUI
-Movement factors
-Frame loss
-Thresholding
-Screen dimensions
-Frame dimensions
-Camera properties
-Common Colors
'''

import time

# Declare if you want to use the GUI.
USEGUI = False

MOVEFACTORX = 0.0020
MOVEFACTORY = 0.0015
LOSTRATIO = 0.005
IMGTHRESH = 125

LOSTCOUNT = 0 #Always initialize at 0
START = time.time()

# A percentage of frame height
VERTDIM = 240  #height of test images
HORDIM = 320     #width of test images
CENX, CENY = HORDIM/2, VERTDIM/2
VERTTHRESHSTART = 0.10 * VERTDIM   #image offset to start trigger verticle movement
HORTHRESHSTART = 0.20 * HORDIM     #image offset to start horizontal movement
VERTTHRESHSTOP = 0.05 * VERTDIM   #image offset to stop trigger vert movement (should be < Start)
HORTHRESHSTOP = 0.10 * HORDIM     #image offset to stop horiz movement (should be < Start)
CHECK = 1
ISO = 200

# Important Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
