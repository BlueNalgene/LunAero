'''
Minimal working version of image tracking using Pi Cam
'''

import io
from time import sleep
import numpy as np
import cv2
import RPi.GPIO as GPIO #RPi GPIO controller
import picamera

if __name__ == '__main__':
	try:
		DATA = io.BytesIO()
		with picamera.PiCamera() as picam:
			picam.capture(DATA, format='jpeg')
		DATA = np.fromstring(DATA.getvalue(), dtype=np.uint8)
		IMAGE = cv2.imdecode(DATA, 1)
		cv2.imwrite('debugimage.jpg', IMAGE)
		CAMERA = picam.OpenCVCapture()
		RET, IMAGE = CAMERA.read()
		IMAGE = cv2.cvtColor(IMAGE, cv2.COLOR_RGB2GRAY)
		THRESH = 127
		MAX_VALUE = 255

		if RET:
			# The frame is ready and already captured
			#cv2.imshow('frame', gray)
			POS_FRAME = IMAGE.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)

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
			CX = int(M['m10']/M['m00'])
			CY = int(M['m01']/M['m00'])

			HEIGHT, WIDTH, CHANNELS = IMAGE.shape
			WIDTH = WIDTH/2
			HEIGHT = HEIGHT/2

			#Check which how motors need to move to put moon in center
			if CX < WIDTH:
				print "pan camera RIGHT"
				sleep(0.05)
				GPIO.output(13, GPIO.LOW)
			elif CX > WIDTH:
				print "pan camera LEFT"
				GPIO.output(15, GPIO.HIGH)
				sleep(0.05)
				GPIO.output(15, GPIO.LOW)
			else:
				print "Center X"
			if CY < HEIGHT:
				print "pan camera DOWN"
				GPIO.output(16, GPIO.HIGH)
				sleep(0.05)
				GPIO.output(16, GPIO.LOW)
			elif CY > HEIGHT:
				print "pan camera UP"
				GPIO.output(18, GPIO.HIGH)
				sleep(0.05)
				GPIO.output(18, GPIO.LOW)
			else:
				print "Center Y"
			#cv2.imshow("Contour",frame)
		else:
			# The next frame is not ready, so we try to read it again
			IMAGE.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, POS_FRAME-1)
			print "frame is not ready"
			# It is better to wait for a while for the next frame to be ready
			cv2.waitKey(1000)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			print 'done'

	except KeyboardInterrupt:
		print 'exiting'
	except:
		print 'An Unknown Error Occurred.  Helpful, right?'
	finally:
#		GPIO.cleanup()
		cv2.destroyAllWindows()
