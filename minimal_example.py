import cv2
from time import sleep
import numpy as np
import picam
import RPi.GPIO as GPIO #RPi GPIO controller

if __name__ == '__main__':
	try:
		camera = picam.OpenCVCapture()
		ret, image = camera.read()
		image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
		thresh = 127
		maxValue = 255

		if ret:
				# The frame is ready and already captured
				#cv2.imshow('frame', gray)

				#This is the meat.  It processes the grayscale'd frame for contours based on the threshold info.
				th, dst = cv2.threshold(image, thresh, maxValue, cv2.THRESH_BINARY)
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

				height, width, channels = frame.shape
				whalf = width/2
				hhalf = height/2

				#Check which how motors need to move to put moon in center
				if cx < whalf:
					print "pan camera RIGHT"
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
				#cv2.imshow("Contour",frame)
			else:
				# The next frame is not ready, so we try to read it again
				image.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
				print "frame is not ready"
				# It is better to wait for a while for the next frame to be ready
				cv2.waitKey(1000)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
except KeyboardInterrupt:
	print 'exiting'
except picamera.PiCameraMMALError:
	print 'MMAL Error Occurred, but the program will be shutting down correctly'
except:
	print 'An Unknown Error Occurred.  Helpful, right?'
finally:
#	image.release()
	RAWCAPTURE.truncate(0)
	GPIO.cleanup()
	cv2.destroyAllWindows()
