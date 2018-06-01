#!/bin/usr/python3

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi
'''

from __future__ import print_function
import time
import sys
import pygame
import cv2
from PIL import Image

from LunCV import Manipulations

outvid = cv2.VideoWriter('/media/wes/ExtraDrive1/mediaout.mp4', 0X00000021, 29.97, (2020, 1080))

def main():
	'''This is the main function
	It activates the Pygame interface and calls other things
	'''

	pos_frame = 0
	
	try:
		while True:
			frame = runner(pos_frame)
			pos_frame = pos_frame + 1
			if pos_frame % 100 == 0:
				print(pos_frame)
			#cv2.namedWindow("Mother", cv2.WINDOW_NORMAL)
			#cv2.resizeWindow("Mother", 1920, 1080)
			#cv2.imshow("Mother", frame)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				return
	except Exception as errorflag:
		errorflag = sys.exc_info()[0]
		print('\033[91m'+ "Error: %s" % errorflag + '\033[0m')
		raise
	finally:
		print("Program ended on frame ", str(pos_frame))
		cv2.destroyAllWindows()

def runner(pos_frame):
	'''Runs the script with appropriate manipulation
	'''
	#CAP = cv2.VideoCapture('/home/wes/Documents/alt/Migrants.mp4')
	#### IT IS ABOUT 132000 FRAMES
	CAP = cv2.VideoCapture('/media/wes/ExtraDrive1/1524943548outA.mp4')
	CAP.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
	ret, frame = CAP.read()
	if ret:
		LCV = Manipulations()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (5, 5), 0)
		lower_thresh, upper_thresh = LCV.magic_thresh(gray)
		contours = LCV.cv_contour(gray, lower_thresh, upper_thresh)
		ellipse, result = LCV.center_moon(frame, contours)
		frame_1 = result[0:1080, 405:1415]
		result = LCV.subtract_background(result)
		result = LCV.halo_noise(ellipse, result)
		contours = LCV.cv_contour(result, 0, 255)
		size_list, centers = LCV.cntsize(contours)
		result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
		frame_2 = result[0:1080, 405:1415]
		#for i in range(0, len(size_list)):
			#cv2.circle(result, (int(centers[i][0]), int(centers[i][1])), int(size_list[i]/2), (255, 0, 255), 2)
			#print(pos_frame, ",", centers[i][0][0], ",", centers[i][1][0], ",", size_list[i])
		##cv2.imwrite('current.png', frame)
		frame_1, frame_2 
		frame = cv2.hconcat((frame_1, frame_2))
		outvid.write(frame)
		return frame
	else:
		return

if __name__ == '__main__':
	main()
