#!/usr/bin/python

"""
# This is a test program for the LunAero project which is able to:
#  - Locate the moon or a simulated moon from a sample image
#  - Track the motion of the moon from the center of the screen
#  - Record video of the process

"""

import time
import sys
import subprocess

import picamera
from scipy import ndimage
from PIL import Image
import numpy as np
import RPi.GPIO as GPIO

# Defines the pins being used for the GPIO pins.
print "Defining GPIO pins"
GPIO.setmode(GPIO.BOARD)
XPIN1 = 15
XPIN2 = 16
XPINP = 18
YPIN1 = 13
YPIN2 = 12
YPINP = 11

# Setup GPIO and start them with 'off' values
PINS = (XPIN1, XPIN2, XPINP, YPIN1, YPIN2, YPINP)
for i in PINS:
	GPIO.setup(i, GPIO.OUT)
	if i != XPINP or YPINP:
		GPIO.output(i, GPIO.LOW)
	else:
		GPIO.output(i, GPIO.HIGH)

# Sets up an output file labeled with the current unixtime
print "Preparing OUTFILE"
OUTFILE = int(time.time())
OUTFILE = str(OUTFILE) + 'out.h264'
subprocess.call(['touch', str(OUTFILE)])
print "OUTFILE will be: " + str(OUTFILE)

def main():
	'''This is the main chunk of the program
	It starts the recording, calls the function, and quits at the end.
	'''
	with picamera.PiCamera() as camera:
		try:
			camera.resolution = (800, 600)
			camera.start_preview()
			camera.start_recording(OUTFILE)
			while True:
				camera.wait_recording(10)
				camera.capture('debugimage.jpg', use_video_port=True)
				image_test()
		except Exception as exep:
	#		print 'An Unknown Error Occurred.  Helpful, right?'
			exep = sys.exc_info()[0]
			print '\033[91m'+ "Error: %s" % exep + '\033[0m'
			raise
		finally:
			camera.stop_recording()
			GPIO.cleanup()

def image_test():
	'''This section controls the GPIO pin movement
	Considers the center of mass of a black and white version of the image.
	Determines the moments of a simple frame, and their XY coordinate
	Check which and how motors need to move to put moon in center
	'''
	img = Image.open('debugimage.jpg')
	img = img.convert('L')
	img = img.point(lambda x: 0 if x < 128 else 255, '1')
	arm = np.asarray(img)
	width, height = img.size
	width = width/2
	height = height/2
	cmy, cmx = ndimage.measurements.center_of_mass(arm)
	# cmy and cmx are from top left, starting at 0
	# Print statements are for hardware debugging.
	if cmx < width:
		print "pan camera RIGHT"
		movex = True
		state = (GPIO.LOW, GPIO.HIGH, GPIO.HIGH)
	elif cmx > width:
		print "pan camera LEFT"
		movex = True
		state = (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
	else:
		print "Center X"
		movex = True
		state = (GPIO.LOW, GPIO.LOW, GPIO.HIGH)
	motor(movex, state)

	if cmy > height:
		print "pan camera DOWN"
		movex = False
		state = (GPIO.LOW, GPIO.HIGH, GPIO.HIGH)
	elif cmy < height:
		print "pan camera UP"
		movex = False
		state = (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
	else:
		print "Center Y"
		movex = False
		state = (GPIO.LOW, GPIO.LOW, GPIO.HIGH)
	motor(movex, state)

def motor(movex, state):
	'''This sends the information to the gearmotors.
	Programming is designed for TB6612FNG
	'''
	if movex:
		GPIO.output(XPIN1, state[0])
		GPIO.output(XPIN2, state[1])
		GPIO.output(XPINP, state[2])
	if not movex:
		GPIO.output(YPIN1, state[0])
		GPIO.output(YPIN2, state[1])
		GPIO.output(YPINP, state[2])
	time.sleep(0.05)
	return


if __name__ == '__main__':
	main()
