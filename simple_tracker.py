#!/usr/bin/python

"""
# This is a test program for the LunAero project which is able to:
#  - Locate the moon or a simulated moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen


# Includes code from speed-cam.py by Calude Pageau
# https://github.com/pageauc/rpi-speed-camera/tree/master/
"""

#-----------------------------------------------------------------------------------------------

# Package Imports
import time
from time import sleep
from threading import Thread #Handler for videostream thread
import numpy as np
import cv2 #OpenCV
import RPi.GPIO as GPIO #RPi GPIO controller
from picamera import PiCamera #RPi Camera
from picamera.array import PiRGBArray #Required to capture frames as arrays


# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) # A PWM
GPIO.setup(12, GPIO.OUT) # A input 2
GPIO.setup(13, GPIO.OUT) # A input 1
GPIO.setup(15, GPIO.OUT) # B input 1
GPIO.setup(16, GPIO.OUT) # B input 2
GPIO.setup(18, GPIO.OUT) # B PWM

# Start GPIO with 'off' values
GPIO.output(11, GPIO.HIGH)
GPIO.output(12, GPIO.LOW)
GPIO.output(13, GPIO.LOW)
GPIO.output(15, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(18, GPIO.HIGH)

# Video Stream Variables
RESOLUTION = (1440, 1080)
FRAMERATE = 30

# Location of movie file if using a pre-captured simulation or training video
# NOTE: If you have a Pi Camera attached to your RPi, it will use it before using 'cap'
#cap = cv2.VideoCapture('testmoonvie.mov')

PiCamera().resolution = RESOLUTION
#PiCamera().rotation = ROTATION
PiCamera().framerate = FRAMERATE
#PiCamera().hflip = HFLIP
#PiCamera().vflip = VFLIP
RAWCAPTURE = PiRGBArray(PiCamera(), size=RESOLUTION)
#stream = PiCamera().capture_continuous(rawCapture, format="bgr", use_video_port=True)
time.sleep(0.1)


#---------
# Define Motor Movements
def vert_cw():
	"""
	Moves vertical motor clockwise
	PWM on 1 low 2 high
	"""
	GPIO.output(13, GPIO.LOW) #1
	GPIO.output(12, GPIO.HIGH) #2
	GPIO.output(11, GPIO.HIGH) #pwm

def horz_cw():
	"""
	Moves horizontal motor clockwise
	PWM on 1 low 2 high
	"""
	GPIO.output(15, GPIO.LOW) #1
	GPIO.output(16, GPIO.HIGH) #2
	GPIO.output(18, GPIO.HIGH) #pwm

def vert_ccw():
	"""
	Moves vertical motor counter-clockwise
	PWM on 1 high 2 low
	"""
	GPIO.output(13, GPIO.HIGH) #1
	GPIO.output(12, GPIO.LOW) #2
	GPIO.output(11, GPIO.HIGH) #pwm

def horz_ccw():
	"""
	Moves orizontal motor counter-clockwise
	PWM on 1 high 2 low
	"""
	GPIO.output(15, GPIO.HIGH) #1
	GPIO.output(16, GPIO.LOW) #2
	GPIO.output(18, GPIO.HIGH) #pwm

def vert_brake():
	"""
	Brakes vertical motor
	PWM off 1 high 2 high
	"""
	GPIO.output(13, GPIO.HIGH) #1
	GPIO.output(12, GPIO.HIGH) #2
	GPIO.output(11, GPIO.LOW) #pwm

def horz_brake():
	"""
	Brakes orizontal motor
	PWM off 1 high 2 high
	"""
	GPIO.output(15, GPIO.HIGH) #1
	GPIO.output(16, GPIO.HIGH) #2
	GPIO.output(18, GPIO.LOW) #pwm

def vert_off():
	"""
	Turns vertical motor off
	PWM on 1 low 2 low
	"""
	# PWM on 1 high 2 low
	GPIO.output(13, GPIO.LOW) #1
	GPIO.output(12, GPIO.LOW) #2
	GPIO.output(11, GPIO.HIGH) #pwm

def horz_off():
	"""
	Turns horizontal motor off
	PWM on 1 low 2 low
	"""
	GPIO.output(15, GPIO.LOW) #1
	GPIO.output(16, GPIO.LOW) #2
	GPIO.output(18, GPIO.HIGH) #pwm


try:
	while True:
		for f in PiCamera().capture_continuous(RAWCAPTURE, format="bgr", use_video_port=True):
			image = f.array
			horz_off()
			vert_off()
			ret, frame = image.read()

			#Defines some important things
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			thresh = 127
			maxValue = 255

			if ret:
				# The frame is ready and already captured
				#cv2.imshow('frame', gray)

				#This determines the frame number
				#pos_frame = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
				#print str(pos_frame)+" frames"

				#This is the meat.  It processes the grayscale'd frame for contours based on the threshold info.
				th, dst = cv2.threshold(gray, thresh, maxValue, cv2.THRESH_BINARY)
				contours, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
				dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
				#Then we draw the contour on the color original
				cv2.drawContours(frame, contours, -1, (255, 255, 0), 3)

				#Considers the first contour detected in a frame.
				cnt = contours[0]

				#Determines the moments of the contoured shape in the frame, and their XY coordinate
				M = cv2.moments(cnt)
				cx = int(M['m10']/M['m00'])
				cy = int(M['m01']/M['m00'])

				#Math to determine roundness
				#area = cv2.contourArea(cnt)
				#peri = cv2.arcLength(cnt,True)
				#arrr = peri/(2*np.pi)
				#print str(cx) + " and " + str(cy) + " and " + str(height) + "," + str(width)

				height, width, channels = frame.shape
				whalf = width/2
				hhalf = height/2

				#Check which how motors need to move to put moon in center
				if cx < whalf:
					print "pan camera RIGHT"
					horz_cw()
					sleep(0.05)
					GPIO.output(13, GPIO.LOW)
				elif cx > whalf:
					print "pan camera LEFT"
					GPIO.output(15, GPIO.HIGH)
					sleep(0.05)
					GPIO.output(15, GPIO.LOW)
				else:
					print "Center X"
				if cy < hhalf:
					print "pan camera DOWN"
					GPIO.output(16, GPIO.HIGH)
					sleep(0.05)
					GPIO.output(16, GPIO.LOW)
				elif cy > hhalf:
					print "pan camera UP"
					GPIO.output(18, GPIO.HIGH)
					sleep(0.05)
					GPIO.output(18, GPIO.LOW)
				else:
					print "Center Y"
				#cv2.imshow("Contour",frame
			else:
				# The next frame is not ready, so we try to read it again
				image.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
				print "frame is not ready"
				# It is better to wait for a while for the next frame to be ready
				cv2.waitKey(1000)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
except KeyboardInterrupt:
	GPIO.cleanup()
image.release()
RAWCAPTURE.truncate(0)
GPIO.cleanup()
cv2.destroyAllWindows()

#-----------------------------------------------------------------------------------------------
# From https://github.com/jrosebr1/imutils
