#!/usr/bin/python

"""
# This is a test program for the LunAero project which is able to:
#  - Locate the moon or a simulated moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen
"""

#-----------------------------------------------------------------------------------------------

# Package Imports
import os
import sys
import io
import time
import subprocess

import numpy as np
import cv2
import RPi.GPIO as GPIO #RPi GPIO controller
import picamera

# Be sure we have access to GPIOmem
if "root gpio" not in (subprocess.check_output(['ls', '-l', '/dev/gpiomem'])):
	subprocess.call(['sudo', 'chmod', 'g+rw' '/dev/gpiomem'])
	subprocess.call(['sudo', 'chown', 'root.gpio' '/dev/gpiomem'])

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


OUTFILE = int(time.time())
OUTFILE = str(OUTFILE) + 'out.mp4'
subprocess.call(['touch', str(OUTFILE)])

if __name__ == '__main__':
	try:
		while True:

			DATA = io.BytesIO()
			with picamera.PiCamera() as picam:
				picam.capture(DATA, format='jpeg', use_video_port=False, resize=(1920, 1080))
			DATA = np.fromstring(DATA.getvalue(), dtype=np.uint8)
			IMAGE = cv2.imdecode(DATA, 1)
			cv2.imwrite('debugimage.jpg', IMAGE)
	#		CAMERA = picam.OpenCVCapture()
	#		RET, IMAGE = cv2.imread()
			IMAGE = cv2.cvtColor(IMAGE, cv2.COLOR_RGB2GRAY)
			THRESH = 127
			MAX_VALUE = 255

			#This is the meat.  It processes the grayscale'd frame for contours based on the THRESHold info.
			TH, DST = cv2.threshold(IMAGE, THRESH, MAX_VALUE, cv2.THRESH_BINARY)
			CONTOURS, HIERARCHY = cv2.findContours(DST, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			DST = cv2.cvtColor(DST, cv2.COLOR_GRAY2BGR)

			#Then we draw the contour on the color original
			cv2.drawContours(IMAGE, CONTOURS, -1, (255, 255, 0), 3)

			#Considers the first contour detected in a frame.
			CNT = CONTOURS[0]

			#Determines the moments of the contoured shape in the frame, and their XY coordinate
			M = cv2.moments(CNT)
			if int(M['m00']) != 0:
				CX = int(M['m10']/M['m00'])
				CY = int(M['m01']/M['m00'])

				HEIGHT, WIDTH = IMAGE.shape
				WIDTH = WIDTH/2
				HEIGHT = HEIGHT/2

				#Check which how motors need to move to put moon in center
				if CX < WIDTH:
					print "pan camera RIGHT"
					GPIO.output(15, GPIO.LOW) #1
					GPIO.output(16, GPIO.HIGH) #2
					GPIO.output(18, GPIO.HIGH) #pwm
					time.sleep(0.05)
					#GPIO.output(18, GPIO.LOW)
				elif CX > WIDTH:
					print "pan camera LEFT"
					GPIO.output(15, GPIO.HIGH) #1
					GPIO.output(16, GPIO.LOW) #2
					GPIO.output(18, GPIO.HIGH) #pwm
					time.sleep(0.05)
					#GPIO.output(18, GPIO.LOW)
				else:
					print "Center X"
					GPIO.output(15, GPIO.LOW) #1
					GPIO.output(16, GPIO.LOW) #2
					GPIO.output(18, GPIO.HIGH) #pwm
				if CY < HEIGHT:
					print "pan camera DOWN"
					GPIO.output(13, GPIO.LOW) #1
					GPIO.output(12, GPIO.HIGH) #2
					GPIO.output(11, GPIO.HIGH) #pwm
					time.sleep(0.05)
					#GPIO.output(16, GPIO.LOW)
				elif CY > HEIGHT:
					print "pan camera UP"
					GPIO.output(13, GPIO.HIGH) #1
					GPIO.output(12, GPIO.LOW) #2
					GPIO.output(11, GPIO.HIGH) #pwm
					time.sleep(0.05)
					#GPIO.output(18, GPIO.LOW)
				else:
					print "Center Y"
					GPIO.output(13, GPIO.LOW) #1
					GPIO.output(12, GPIO.LOW) #2
					GPIO.output(11, GPIO.HIGH) #pwm

			if os.path.isfile(OUTFILE) is True:
				subprocess.call(['ffmpeg', '-loglevel', 'quiet', '-y', '-i', 'debugimage.jpg', '-c:v',
						'libx264', '-filter_complex', '[0] concat=n=1:v=1:a=0 [v]', '-map', '[v]',
						str(OUTFILE)], stdout=open(os.devnull, 'w'))
			else:
				subprocess.call(['ffmpeg', '-loglevel', 'quiet', 'y', '-i', str(OUTFILE), '-i', 'debugimage.jpg',
						'-c:v', 'libx264', '-filter_complex', '"[0][1] concat=n=2:v=1:a=0 [v]"',
						'-map', '"[v]"', str(OUTFILE)], stdout=open(os.devnull, 'w'))

			if cv2.waitKey(1) & 0xFF == ord('q'):
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
