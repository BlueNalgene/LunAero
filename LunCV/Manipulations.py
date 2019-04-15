#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is a test program for the LunAero project which is able to:
 - Locate a simplified moon
 - Put a contour around the moon
 - Track the motion of the moon from the center of the screen

This particular file centers the moon and subtracks the background.
'''

import numpy as np

import cv2

class Manipulations():
	'''Begin class
	'''
	# Background removal based on
	# An improved adaptive background mixture model for real-time tracking with shadow detection"
	# by P. KadewTraKuPong and R. Bowden in 2001.
	FGBG = cv2.bgsegm.createBackgroundSubtractorMOG(100, 7, 0.5, 5)
	MAT = np.ones((3, 3), np.uint8)

	def __init__(self):
		'''Null
		'''

	def center_moon(self, frame, contours):
		'''This function finds the light source in a frame and centers it.
		'''
		ret = True
		if contours:
			# We only care about the BIGGEST contour here
			ellipse = max(contours, key=cv2.contourArea)

			# We treat it as an ellipse to account for irregularities in shape.
			# Based on Andrew W Fitzgibbon and Robert B Fisher. A buyer's guide to conic fitting.
			# In Proceedings of the 6th British conference on Machine vision (Vol. 2),
			# pages 513–522. BMVA Press, 1995.
			ellipse = cv2.fitEllipse(ellipse)

			# This makes an 'image' of all nothing with the same size as the original
			mask = np.zeros(frame.shape, dtype=np.uint8)
			# This draws the ellipse onto the empty shape we just made.
			# The parameters are from the fitEllipse, but they have to be INT.
			cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]/2), \
							int(ellipse[1][1]/2)), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
			result = frame & mask
			# Now the mask is shifted such that the center of the ellipse is in the center of the
			# screen.
			col = len(frame[0])
			row = len(frame)
			xdi = (col / 2) - int(ellipse[0][0])
			ydi = (row / 2) - int(ellipse[0][1])
			mmm = np.float32([[1, 0, xdi], [0, 1, ydi]])
			result = cv2.warpAffine(result, mmm, (col, row))
		else:
			ret = False
		return ret, ellipse, result


	def subtract_background(self, result):
		'''This function removes the background from a frame.
		It is strongly recommended this only be done with STILL frames.
		Otherwise it will be a mess.

		learningRate = 0.05 deals with moon features better, but may be too taxing for Pi
		The gradient morph is required for self.FGBG
		Then we blur what we have before thresholding
		'''
		result = self.FGBG.apply(result, learningRate=.05)
		result = cv2.morphologyEx(result, cv2.MORPH_GRADIENT, self.MAT)
		#result = cv2.GaussianBlur(result, (5, 5), 0)
		return result

	def magic_thresh(self, frame):
		'''Use a GRAY frame for "frame" here.
		It will output some magical threshold values
		which can be used for bandpass filtering
		'''
		vvv = np.mean(frame)
		lower_thresh = int(max(0, 0.67 * vvv))
		upper_thresh = int(min(255, 1.33 * vvv))
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
		_, contours, _ = cv2.findContours(thresh, 2, 1)
		#_, contours, hierarchy = cv2.findContours(thresh, 2, 1)
		return contours

	def cntsize(self, contours):
		'''Makes a list of contour sizes
		'''
		centers = []
		size_list = []
		if contours:
			cnt = contours[0]
			for cnt in contours:
				perimeter = cv2.arcLength(cnt, True)
				if perimeter > 8 and perimeter < 200:
					(xxx, yyy), radius = cv2.minEnclosingCircle(cnt)
					centroid = (int(xxx), int(yyy))
					radius = int(radius)
					centroid = np.array([[xxx], [yyy]])
					centers.append(np.round(centroid))
					size_list.append(np.round(perimeter))
		return size_list, centers
