#!/bin/usr/python

from imutils.video import VideoStream
import imutils
import cv2
import argparse
import time

vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

while True:
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	print "hats"
	cv2.imwrite('debugimage.jpg', frame)
	cv2.imshow("frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
cv2.destroyAllWindows()
vs.stop()
