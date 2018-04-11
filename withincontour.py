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

#cap = cv2.VideoCapture('statmoonwbirds.mov')
cap = cv2.VideoCapture('Migrants.mp4')
#cap = cv2.VideoCapture('Nocturnal.mp4')

#This is the background removing step
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(100, 7, 0.5, 5)

#This defines a matrix for other functions
mat = np.ones((3, 3), np.uint8)

def main():
	'''This is the main function of the code.
	'''
	try:
		while cap.isOpened():
			ret, frame = cap.read()
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		if ret:
			cv_contour()
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
		else:
			# The next frame is not ready, so we try to read it again
			cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
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
		cap.release()
		cv2.destroyAllWindows()

def cv_manip():
	'''This function is where image manipulation happens.
	This is currently unused
	'''
	blurred = cv2.GaussianBlur(gray, (3, 3), 0)
	can = cv2.Canny(blurred, 5, 200)
	fgmask = cv2.addWeighted(fgmask, 0.5, can, 0.5, 0)
	fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_GRADIENT, mat)

def cv_contour():
	'''This function takes care of contour selections
	'''
	ret, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
	_, contours, hierarchy = cv2.findContours(thresh, 2, 1)

	# We only care about the BIGGEST contour here
	c = max(contours, key = cv2.contourArea)

	# We treat it as an ellipse to account for irregularities in shape.
	ellipse = cv2.fitEllipse(c)

	# This makes an 'image' of all nothing with the same size as the original
	mask = np.zeros(frame.shape, dtype=np.uint8)
	# This draws the ellipse onto the empty shape we just made.
	# The parameters are from the fitEllipse, but they have to be INT.
	cv2.ellipse(mask, (int(ellipse[0][0]), int(ellipse[0][1])), (int(ellipse[1][0]), int(ellipse[1][1])), int(ellipse[2]), 0, 360, (255, 255, 255), -1, 8)
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
	result = fgbg.apply(result, learningRate=.1)
	#result = cv2.GaussianBlur(result, (3, 3), 0)
	#can = cv2.Canny(result, 5, 200)
	#result = cv2.addWeighted(result,0.5,can,0.5,0)
	result = cv2.morphologyEx(result, cv2.MORPH_GRADIENT, mat)

	# Retest the image for contours
	#gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
	ret, thresh = cv2.threshold(result, 127, 255, cv2.THRESH_BINARY)
	_, contours, hierarchy = cv2.findContours(thresh, 2, 1)
	return result, frame

			#ret,thresh = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
			#contours,hierarchy = cv2.findContours(thresh, 3, 2)
			#nocolor = cv2.cvtColor(fgmask, cv2.COLOR_BGR2GRAY)

			##This if is required to ignore initial frames
			#if not contours:
				#pass
			#else:
				#cnt = contours[0]
				#i = 0
				#for cnt in contours:
					#if len(cnt) <= 5:
						#pass
					#else:
						#ellipse = cv2.fitEllipse(cnt)
						#cv2.ellipse(frame,ellipse,(255,0,0),2)

						#print(str('FRAME')+str(ellipse[0][0])+','+str(ellipse[0][1])+','+str(ellipse[1][0])+','+str(ellipse[1][1])+','+str(ellipse[2]))

						#M = cv2.moments(cnt)
						#if M['m00'] == 0:
							#pass
						#else:
							#cx = int(M['m10']/M['m00'])
							#cy = int(M['m01']/M['m00'])

						##for each pixel in the array, check to see if it is inside the ellipse
						##The equation for a shifted ellipse:
						## 1 = (((x-c_x)^2)/(a^2))+(((y-c_y)^2)/(b^2))
						##Note that Python uses 24 bytes for both floats and ints.  Using funny math for decimals
						##   is not beneficial for us.  Therefore, I will be using floats.  Note, that if you want
						##   to look at very large images, you will have to change this (and not use a raspi).
						##The row-by-row nature of this calc means we are going to just get the bounds of the
						##   ellipse for a single row of data, rather than find a perimeter properly.
						##
						## This is currently a placeholder for the stuff from "newtest.py"
						#pptout = 1

						##if the pixel is NOT in the ellipse, pass
						#if pptout == 0:
							#pass

						##else the pixel is in the ellipse.  Therefore we are going to do things to it.
						#else:
							##adjust the pixel to a new coordinate with respect to the center of moment
							##
							## This is a new thing I'm not so sure of to rotate the array
							## ndi.rotate(input, angle)
							## I need to see if this rotates from the center of mass of the image.  It may
							## make the moment unneccessary.  I assume CW rotation?
							#pass

						## execute fbgb on the elliptical map
						## find contours again
						## if there are no contours, pass
						## else there are contours

							## we circle these contours (for now) This is where the ID will come later
						## we put these contours back on the original

				#i = 1 + i

				## Initialize empty list
				##lst_intensities = []

				### For each list of contour points...
				##for i in range(len(cnt)):
					### Create a mask image that contains the contour filled in
					##cimg = np.zeros_like(frame)
					##cv2.drawContours(cimg, cnt, i, color=255, thickness=-1)

				### Access the image pixels and create a 1D numpy array then add to list
				##pts = np.where(cimg == 255)
				##lst_intensities.append(frame[pts[0], pts[1]])

		##### learningRate = 0.05 deals with moon features better, but may be too taxing for Pi
		####fgmask = fgbg.apply(frame, learningRate=.1)

		#####This is where any image manipulation happens
		####blurred = cv2.GaussianBlur(gray, (3, 3), 0)
		####can = cv2.Canny(blurred, 5, 200)
		####fgmask = cv2.addWeighted(fgmask,0.5,can,0.5,0)
		####fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_GRADIENT, mat)

				##### Three different hierarchal levls get circled in different colors

					####if hierarchy[0][i][3] == (-1):
						####(x,y),radius = cv2.minEnclosingCircle(cnt)
						####center = (int(x),int(y))
						####radius = int(radius)
						####cv2.circle(frame,center,radius,(0,255,0),2)
					####elif hierarchy[0][i][3] == 0:
						####(x,y),radius = cv2.minEnclosingCircle(cnt)
						####center = (int(x),int(y))
						####radius = int(radius)
						####cv2.circle(frame,center,radius,(255,255,0),2)
					####elif hierarchy[0][i][3] <= 1:
						####(x,y),radius = cv2.minEnclosingCircle(cnt)
						####center = (int(x),int(y))
						####radius = int(radius)
						####cv2.circle(frame,center,radius,(0,0,255),2)


if __name__ == '__main__':
	main()
