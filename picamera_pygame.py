#!/usr/bin/python

"""A simple script to get the picamera output working in a pygame interface
"""

#import argparse
import sys
import io
from time import sleep

import numpy as np
import cv2
import picamera
import pygame
from pygame.locals import *

pygame.display.init()
DISPLAYSURF = pygame.display.set_mode((1920,1080))
pygame.display.set_caption('Hello PiCamera World!')
DATA = io.BytesIO()
while True:
	try:
		with picamera.PiCamera() as picam:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
			picam.capture(DATA,
				format='jpeg',
				use_video_port=False,
				resize=(1920,1080))
			DATA = np.fromstring(DATA.getvalue(), dtype=np.uint8)
			IMAGE = cv2.cvtColor(IMAGE, cv2.COLOR_RGB2GRAY)
			THRESH = 127
			MAX_VALUE = 255
			TH, DST = cv2.threshold(IMAGE,
						THRESH,
						MAX_VALUE,
						cv2.THRESH_BINARY)
			CONTOURS, HIERARCHY = cv2.findContours(DST,
								cv2.RETR_TREE,
								cv2.CHAIN_APPROX_SIMPLE)
			DST = cv2.cvtColor(DST, cv2.COLOR_GRAY2BGR)
			cv2.drawContours(IMAGE, CONTOURS, -1, (255, 255, 0), 3)
			CNT = CONTOURS[0]
			IMAGE = cv2.imwrite('temp.jpg', IMAGE)
			IMAGE = pygame.image.load(IMAGE)
			gameDisplay.blit(IMAGE, (960,540))
			if cv2.waitKey(1) & 0xFF == ord('q'):
				print 'done'
		pygame.display.update()

	except KeyboardInterrupt:
		print 'exiting'
	except Exception as e:
		e = sys.exc_info()[0]
		print '\033[91m' + "Error: %s" % e + '\033[0m'
		raise
	finally:
		cv2.destroyAllWindows()
		pygame.quit()
		sys.exit()
