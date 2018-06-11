#!/bin/usr/python3

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi
'''

from __future__ import print_function

# Define if you want to use the GUI.
USEGUI = False

import math
import numpy as np
#from PIL import Image
if USEGUI:
	import pygame

import cv2

from LunCV import Manipulations
if USEGUI:
	from LunCV import Gui

#Initialize these variables
SIZE_LIST = []
SIZE_LIST_OLD = []
SIZE_LIST_OLD_OLD = []
CENTERS = []
CENTERS_OLD = []
CENTERS_OLD_OLD = []

def main():
	'''This is the main function
	'''
	status_flag = True

	if USEGUI:
		status_flag = False
		gui = Gui()
		status_flag = gui.initialize_gui(status_flag)

	pos_frame = 0

	while status_flag:
		if USEGUI:
			gui.frame_number(pos_frame)
		frame, result = runner(pos_frame)
		if USEGUI:
			pos_frame, status_flag = gui.frame_display(pos_frame, frame, result)
		pos_frame = pos_frame + 1

	print("Program ended on frame ", str(pos_frame))

def runner(pos_frame):
	'''Runs the script with appropriate manipulation
	'''
	# We need to tell python to use the global declarations from the beginning
	global SIZE_LIST_OLD, CENTERS_OLD, SIZE_LIST_OLD_OLD, CENTERS_OLD_OLD, SIZE_LIST, CENTERS

	#cap = cv2.VideoCapture('/home/wes/Documents/alt/Migrants.mp4')
	#### IT IS ABOUT 132000 FRAMES
	cap = cv2.VideoCapture('/media/wes/ExtraDrive1/1524943548outA.mp4')
	cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
	ret, frame = cap.read()

	if ret:
		lcv = Manipulations()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (5, 5), 0)
		lower_thresh, upper_thresh = lcv.magic_thresh(gray)
		contours = lcv.cv_contour(gray, lower_thresh, upper_thresh)
		ellipse, result = lcv.center_moon(frame, contours)
		result = lcv.subtract_background(result)
		result = lcv.halo_noise(ellipse, result)
		contours = lcv.cv_contour(result, 0, 255)
		SIZE_LIST_OLD = SIZE_LIST
		CENTERS_OLD = CENTERS
		SIZE_LIST, CENTERS = lcv.cntsize(contours)
		fit_score = bird_velocity(pos_frame, contours)
		result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
		#if contours:
			#for i in range(0, len(SIZE_LIST)):
				#if fit_score:
					#if fit_score[i] > 0.5:
						#cv2.circle(result, (int(CENTERS[i][0]), int(CENTERS[i][1])), \
							#int(SIZE_LIST[i]/2), (255, 0, 255), 2)
						#print("ding", fit_score[i])
		##cv2.imwrite('current.png', frame)
	else:
		frame = []
		result = []
	return frame, result

def bird_velocity(pos_frame, contours):
	'''This function will detect birds based on area and velocity of the contour.
	The fitness scoring is based on linear relationship between area and velocity.
	'''
	# We need to tell python to use the global declarations from the beginning
	global SIZE_LIST_OLD, CENTERS_OLD
	# The Area Velocity constants are calculated from the calibration relationship
	av_slope = 1.04605
	av_icept = 12.4457
	speed_factor = 0.5
	area_factor = 0.5
	top = 0
	fit_score = []
	# Initialize empty lists for the scores
	score_speed_group = []
	score_area_group = []
	for i in range(np.size(SIZE_LIST, 0)):
		for j in range(np.size(SIZE_LIST_OLD, 0)):
			try:
				# This equation is the difference between the predicted value of velocity and the observed
				# y = m*x+b - sqrt((x1-x2)**2+(y1-y2)**2)
				score_speed = float(((av_slope*SIZE_LIST_OLD[j])+av_icept) - \
					(math.sqrt((CENTERS[i][0] - CENTERS_OLD[j][0])**2) + \
						((CENTERS[i][1] - CENTERS_OLD[j][1])**2)))
				score_area = (SIZE_LIST[i] - SIZE_LIST_OLD[j])
				# We need to make an equation to test for goodness
				# a*(1/abs(speed))+b*(1/abs(area))
				top = ((speed_factor*(1/(abs(score_speed)+1))) + (area_factor*(1/(abs(score_area)+1))))
				#fit_score.append((top)
				#score_speed_group.append(score_speed)
				#score_area_group.append(score_area)
				if top > 0.25:
					print(pos_frame, CENTERS[i][0][0], CENTERS[i][1][0], SIZE_LIST[i], top, score_speed, score_area)
			except IndexError:
				pass
	#score_speed_group = []
	#score_area_group = []
	if pos_frame > 14999:
		quit()
		#print(top)
		#except ValueError:
			#print("ValueError")
			##print(fit_score)
			##print(score_speed)
			##print(score_area)
			#pass
	#if score_area_group:
		#print(score_area_group)
		#print(score_speed_group)
	#return top
	return fit_score

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("keyboard task kill")
	finally:
		if USEGUI:
			pygame.quit()
