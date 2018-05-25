#!/bin/usr/python3

'''
# This is a test program for the LunAero project which is able to:
#  - Locate a simplified moon
#  - Put a contour around the moon
#  - Track the motion of the moon from the center of the screen

#This particular file centers the moon and subtracks the background.
'''

import sys
import pygame
import numpy as np
import cv2
from scipy import ndimage as ndi

FGBG = cv2.bgsegm.createBackgroundSubtractorMOG(100, 7, 0.5, 5)
MAT = np.ones((3, 3), np.uint8)

class Manipulations():
	def __init__ (self):
		'''Null
		'''

	def center_moon(self, frame, contours):
		'''This function finds the light source in a frame and centers it.
		'''
		if contours:
			# We only care about the BIGGEST contour here
			ellipse = max(contours, key=cv2.contourArea)
			
			# We treat it as an ellipse to account for irregularities in shape.
			ellipse = cv2.fitEllipse(ellipse)

			# This makes an 'image' of all nothing with the same size as the original
			mask = np.zeros(frame.shape, dtype=np.uint8)
			# This draws the ellipse onto the empty shape we just made.
			# The parameters are from the fitEllipse, but they have to be INT.
			cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]/2), \
							int(ellipse[1][1]/2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
			result = frame & mask
			# Now the mask is shifted such that the center of the ellipse is in the center of the screen.
			col = len(frame[0])
			row = len(frame)
			xdi = (col / 2) - int(ellipse[0][0])
			ydi = (row / 2) - int(ellipse[0][1])
			M = np.float32([[1, 0, xdi], [0, 1, ydi]])
			result = cv2.warpAffine(result, M, (col, row))
			return(ellipse, result)

	def subtract_background(self, result):
		'''This function removes the background from a frame.
		It is strongly recommended this only be done with STILL frames.
		Otherwise it will be a mess.
		
		learningRate = 0.05 deals with moon features better, but may be too taxing for Pi
		The gradient morph is required for FGBG
		Then we blur what we have before thresholding
		'''
		result = FGBG.apply(result, learningRate=.05)
		result = cv2.morphologyEx(result, cv2.MORPH_GRADIENT, MAT)
		#result = cv2.GaussianBlur(result, (5, 5), 0)
		return result

	def magic_thresh(self, frame):
		'''Use a GRAY frame for "frame" here.
		It will output some magical threshold values
		which can be used for bandpass filtering
		'''
		v = np.mean(frame)
		lower_thresh = int(max(0, 0.67 * v))
		upper_thresh = int(min(255, 1.33 * v))
		return lower_thresh, upper_thresh

	def halo_noise(self, ellipse, frame):
		'''Requires a BINARY "frame" to work
		Puts a black ellipse over the largest contour.
		Presumably, this is the edge of the moon against the sky
		This minimizes the noise from clouds and haze.
		'''
		mask = np.zeros_like(frame)
		col = len(frame[0])
		row = len(frame)
		cv2.ellipse(mask, (int(col/2), int(row/2)), (int(ellipse[1][0]/2.2), \
						int(ellipse[1][1]/2.2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
		frame = frame & mask
		frame = np.array(frame, np.uint8)
		return frame

	def cv_contour(self, frame, lower_thresh, upper_thresh):
		'''This function takes care of contour selections
		Requires GRAYSCALE
		'''
		_, thresh = cv2.threshold(frame, lower_thresh, upper_thresh, cv2.THRESH_BINARY)
		_, contours, hierarchy = cv2.findContours(thresh, 2, 1)
		return contours

	def cntsize(self, contours):
		centers = []
		size_list = []
		if contours:
			cnt = contours[0]
			for cnt in contours:
				perimeter = cv2.arcLength(cnt, True)
				if perimeter > 8 and perimeter < 200:
					(x, y), radius = cv2.minEnclosingCircle(cnt)
					centroid = (int(x), int(y))
					radius = int(radius)
					centroid = np.array([[x], [y]])
					centers.append(np.round(centroid))
					size_list.append(np.round(perimeter))
		return size_list, centers






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


	if contours:
		# We only care about the BIGGEST contour here
		ellipse = max(contours, key=cv2.contourArea)
		
		# We treat it as an ellipse to account for irregularities in shape.
		ellipse = cv2.fitEllipse(ellipse)

		# This makes an 'image' of all nothing with the same size as the original
		mask = np.zeros(frame.shape, dtype=np.uint8)
		# This draws the ellipse onto the empty shape we just made.
		# The parameters are from the fitEllipse, but they have to be INT.
		cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]/2), \
						int(ellipse[1][1]/2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
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
		print(v)
		lower_thresh = int(max(0, 0.67 * v))
		upper_thresh = int(min(255, 1.33 * v))

		# Retest the image for contours
		_, thresh = cv2.threshold(result, lower_thresh, upper_thresh, cv2.THRESH_BINARY)
		ret, contours, hierarchy = cv2.findContours(thresh, 2, 1)

		# Place a thick black ellipse over the largest contour.  This will
		# act as a mask to cover up the noisy moon edge.
		mask = np.zeros_like(result)
		cv2.ellipse(mask, (int(col/2), int(row/2)), (int(ellipse[1][0]/2.2), \
						int(ellipse[1][1]/2.2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
		result = result & mask
		result = np.array(result, np.uint8)
		return result, frame, contours

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
