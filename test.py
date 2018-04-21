# Package Imports
import os
import sys
import io
import time
import subprocess
from threading import Thread

# Package imports requiring pip installs
import numpy as np
import cv2
import picamera
from picamera.array import PiRGBArray



resolution = (1360, 768)
framerate = 25
with picamera.PiCamera() as picam:
	data = io.BytesIO()
	#raw_capture = PiRGBArray(picam, size=resolution)
	for stream in picam.capture_continuous(data, format="bgr", use_video_port=True):
		data.truncate()
		data.seek(0)
	img=np.asarray(frame.array)
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
		#picam.capture(data, format='jpeg', use_video_port=True)
		#data = np.fromstring(data.getvalue(), dtype=np.uint8)
		#image = cv2.imdecode(data, 1)
		#cv2.imwrite('debugimage.jpg', image)
		#image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
		#return image

#def streamer(resolution, framerate):
	#'''This starts the camera thread and
	#begins running it
	#'''
	#with picamera.PiCamera() as picam:
		#raw_capture = PiRGBArray(picam, size=resolution)
		#stream = picam.capture_continuous(raw_capture, format="bgr", use_video_port=True)
		#frame = None
		#stopped = False
		#thread = Thread(target=update_stream(stream, frame, raw_capture, stopped), args=())
		#thread.daemon = True
		#thread.start()



#def update_stream(stream, frame, raw_capture, stopped):
	#'''This updates the stream from streamer
	#when directed to another thread
	#'''
	#for each in stream:
		#frame = each.array
		#raw_capture.truncate(0)
		#if stopped:
			#stream.close()
			#raw_capture.close()
			#with picamera.PiCamera() as picam:
				#picam.close()
			#return frame
