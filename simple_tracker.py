#!/usr/bin/python

"""
# This is a test program for the LunAero project which is able to:
#  - Locate the moon or a simulated moon from a sample image
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen
#
# Additional Functions include:
#  - Keyboard manual control of motors using arrow key_scanner
#
# TODO:
#  - Make "keyboard period" more obvious.
#  - Record from the picamera video stream as OUTFILE
#  - argparse
"""

#-----------------------------------------------------------------------------------------------

# Package Imports
import os
import sys
import io
import time
import subprocess

# Package imports requiring pip installs
from pynput import keyboard
import numpy as np
import cv2
import RPi.GPIO as GPIO #RPi GPIO controller
import picamera

# Tell Windows users to GTFO
if os.name == 'nt':
	print "Some parts of this program may be incompatible with Windows"

# Detect Raspberry Pi Camera
if "0" in subprocess.check_output(['vcgencmd', 'get_camera']):
	print "You either do not have a RPi camera attached, or it is not enabled."
	print "Try 'sudo raspi-config' and enable camera in the Interfacing Options."

# Be sure we have access to GPIOmem
if "root gpio" not in subprocess.check_output(['ls', '-l', '/dev/gpiomem']):
	subprocess.call(['sudo', 'chmod', 'g+rw', '/dev/gpiomem'])
	subprocess.call(['sudo', 'chown', 'root.gpio', '/dev/gpiomem'])

print "1"

# Defines the pins being used for the GPIO pins.
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
OUTFILE = int(time.time())
OUTFILE = str(OUTFILE) + 'out.mp4'
subprocess.call(['touch', str(OUTFILE)])



def main():
	'''This is the main chunk of the program
	'''
	try:
		cam = picamera.PiCamera()
		cam.resolution(1920, 1080)
		cam.start_recording(OUTFILE)
		while True:

			image = cam_interface()
			contours = cv_magic(image)
			gpio(contours, image)

			if cv2.waitKey(10) & 0xFF == ord('q'):
				print 'done'

	except KeyboardInterrupt:
		print 'exiting'
	except Exception as e:
#		print 'An Unknown Error Occurred.  Helpful, right?'
		e = sys.exc_info()[0]
		print '\033[91m'+ "Error: %s" % e + '\033[0m'
		raise
	finally:
		GPIO.cleanup()
		cv2.destroyAllWindows()

def cam_interface():
	'''This is the interface which pulls an image from the
	Raspberry Pi camera.  It returns the image which we will use a bunch later.
	'''
	data = io.BytesIO()
	with picamera.PiCamera() as picam:
		#picam.resolution = (1920, 1080)
		picam.capture(data, format='jpeg', use_video_port=False, resize=(1920, 1080))
	data = np.fromstring(data.getvalue(), dtype=np.uint8)
	image = cv2.imdecode(data, 1)
	cv2.imwrite('debugimage.jpg', image)
	image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	return image

def cv_magic(image):
	'''This is the meat.
	It processes the grayscale'd frame for contours based on the threshold info.
	Then we draw the contour on the color original
	'''
	thresh = 127
	max_value = 255
	th, dst = cv2.threshold(image, thresh, max_value, cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
	cv2.drawContours(image, contours, -1, (255, 255, 0), 3)
	return contours

def gpio(contours, image):
	'''This section controls the GPIO pin movement
	Considers the first contour detected in a frame.
	Determines the moments of the contoured shape in the frame, and their XY coordinate
	Check which and how motors need to move to put moon in center
	'''

	contours = contours[0]

	m = cv2.moments(contours)

	#The following if prevents and ignores DivideByZero exceptions.
	#This is a quick and dirty fix which is not meant to see the light of day.
	if int(m['m00']) != 0:
		cx = int(m['m10']/m['m00'])
		cy = int(m['m01']/m['m00'])

		height, width = image.shape
		width = width/2
		height = height/2

		# Print statements are for hardware debugging.
		if cx < width:
			print "pan camera RIGHT"
			movex = True
			state = (GPIO.LOW, GPIO.HIGH, GPIO.HIGH)
		elif cx > width:
			print "pan camera LEFT"
			movex = True
			state = (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
		else:
			print "Center X"
			movex = True
			state = (GPIO.LOW, GPIO.LOW, GPIO.HIGH)
		motor(movex, state)

		if cy < height:
			print "pan camera DOWN"
			movex = False
			state = (GPIO.LOW, GPIO.HIGH, GPIO.HIGH)
		elif cy > height:
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

def on_press(key):
	'''Detects the keypresses when enabled.
	And it does things when it works.
	Notably, it moves the motors manaually.
	'''
	try:
		k = key.char
	except:
		k = key.name
	if key == keyboard.Key.esc:
		return False
	if k in ['left', 'right', 'up', 'down']:
		if k in ['left', 'right']:
			if k == 'left':
				print "pan camera LEFT"
				movex = True
				state = (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
				motor(movex, state)
			else:
				print "pan camera RIGHT"
				movex = True
				state = (GPIO.LOW, GPIO.HIGH, GPIO.HIGH)
				motor(movex, state)
		else:
			if k == 'up':
				print "pan camera UP"
				movex = False
				state = (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
				motor(movex, state)
			else:
				print "pan camera DOWN"
				movex = False
				state = (GPIO.LOW, GPIO.HIGH, GPIO.HIGH)
				motor(movex, state)

def key_scanner():
	'''This is a threaded scanning function.
	When this is enabled in the main script, another thread will begin
	polling the keyboard for presses.
	'''
	lis = keyboard.Listener(on_press=on_press)
	lis.start()
	lis.join()
	return

if __name__ == '__main__':
	#key_scanner()
	main()
