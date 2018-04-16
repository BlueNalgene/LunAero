#!/bin/usr/python

'''
# This is a test program for the LunAero project which is able to:
#  - Locate a simplified moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen

#This particular file centers the moon and subtracks the background.
'''

import sys

import numpy as np
import cv2
from scipy import ndimage as ndi

CAP = cv2.VideoCapture('statmoonwbirds.mov')
#CAP = cv2.VideoCapture('Migrants.mp4')
#CAP = cv2.VideoCapture('test.mp4')

#This is the background removing step
FGBG = cv2.bgsegm.createBackgroundSubtractorMOG(100, 7, 0.5, 5)

#This defines a matrix for other functions
MAT = np.ones((3, 3), np.uint8)
MATTWO = np.ones((7, 7), np.uint8)

def main():
	'''This is the main function of the code.
	'''
	try:
		while CAP.isOpened():
			pos_frame = CAP.get(cv2.CAP_PROP_POS_FRAMES)
			ret, frame = CAP.read()

			if ret:
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				#gray = cv_manip(gray)
				gray = cv2.GaussianBlur(gray, (5, 5), 0)
				result, frame = cv_contour(frame, gray)
				cv2.imwrite('current.png', frame)
				# This mess displays different things side by side
				# The Mother window shows the manipulated image that is being used for cakculations
				# The Original window shows the contours overlaid on the original frame
				cv2.namedWindow("Mother", cv2.WINDOW_NORMAL)
				cv2.resizeWindow("Mother", 700, 500)
				cv2.imshow("Mother", result)
				cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
				cv2.resizeWindow("Original", 700, 500)
				cv2.imshow("Original", frame)
				result = cv2.morphologyEx(result, cv2.MORPH_OPEN, MATTWO)
				cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
				cv2.resizeWindow("Test", 700, 500)
				cv2.imshow("Test", result)
			else:
				# The next frame is not ready, so we try to read it again
				CAP.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1)
				print "frame is not ready"
				# It is better to wait for a while for the next frame to be ready
				cv2.waitKey(1000)

			if cv2.waitKey(10) & 0xFF == ord('q'):
				return

	except KeyboardInterrupt:
		print "Exit code issued"
	except Exception as errorflag:
		errorflag = sys.exc_info()[0]
		print '\033[91m'+ "Error: %s" % errorflag + '\033[0m'
		raise
	finally:
		CAP.release()
		cv2.destroyAllWindows()

def cv_manip(gray):
	'''This function is where image manipulation happens.
	This is currently unused
	Also BROKEN, define fgmask
	'''
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	gray = FGBG.apply(blurred, learningRate=.1)	
	can = cv2.Canny(blurred, 5, 200)
	#fgmask = FGBG.apply(can, learningRate=.1)
	#fgmask = cv2.addWeighted(fgmask, 0.5, can, 0.5, 0)
	#fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_GRADIENT, MAT)
	#gray = blurred
	return gray

def cv_contour(frame, gray):
	'''This function takes care of contour selections
	'''
	_, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
	_, contours, hierarchy = cv2.findContours(thresh, 2, 1)

	if contours:
		# We only care about the BIGGEST contour here
		ellipse = max(contours, key=cv2.contourArea)
		
		# We treat it as an ellipse to account for irregularities in shape.
		ellipse = cv2.fitEllipse(ellipse)

		# This makes an 'image' of all nothing with the same size as the original
		mask = np.zeros(frame.shape, dtype=np.uint8)
		# This draws the ellipse onto the empty shape we just made.
		# The parameters are from the fitEllipse, but they have to be INT.
		cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]), \
					int(ellipse[1][1])), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
		result = frame & mask

		# Now the mask is shifted such that the center of the ellipse is in the center of the screen.
		col = len(frame[0])
		row = len(frame)
		xdi = (col / 2) - int(ellipse[0][0])
		ydi = (row / 2) - int(ellipse[0][1])
		M = np.float32([[1, 0, xdi], [0, 1, ydi]])
		result = cv2.warpAffine(result, M, (col, row))

		# Subtract background from stilled frame
		# learningRate = 0.05 deals with moon features better, but may be too taxing for Pi
		result = FGBG.apply(result, learningRate=.05)
		# This is gradient morph is required for FGBG
		result = cv2.morphologyEx(result, cv2.MORPH_GRADIENT, MAT)
		# Blur what we have before thresholding
		result = cv2.GaussianBlur(result, (5, 5), 0)
		
		#Set dynamic threshold 33% on each side of the mean. 
		v = np.mean(gray)
		print v
		lower_thresh = int(max(0, 0.67 * v))
		upper_thresh = int(min(255, 1.33 * v))
		# Retest the image for contours
		_, thresh = cv2.threshold(result, lower_thresh, upper_thresh, cv2.THRESH_BINARY)
		_, contours, hierarchy = cv2.findContours(thresh, 2, 1)
		return result, frame


def size_exclusion(contours, frame):
	'''UNUSED
	This function takes the contours and filters them
	based on perimeter.  If the contour is within a certain
	size, it circles the contour in red on the "frame"
	image.  This can be difficult to see.  The circles
	are mostly for debugging though, so don't worry
	too much about that.  Ensure this is placed after
	cv_contour and before the display in main.
	'''
	#This if is required to ignore initial frames
	if contours:
		cnt = contours[0]
		for cnt in contours:
			perimeter = cv2.arcLength(cnt, True)
			if perimeter > 10 and perimeter < 20:
				(x, y), radius = cv2.minEnclosingCircle(cnt)
				center = (int(x), int(y))
				radius = int(radius)
				cv2.circle(frame, center, radius, (0, 0, 255), 2)
	return frame

if __name__ == '__main__':
	main()
