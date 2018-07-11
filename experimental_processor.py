#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi.  If you choose to run this
on the RasPi, make sure that USEGUI in ./__init__.py is False.
'''

from __future__ import print_function

import csv
import itertools
import math
import os
#from PIL import Image
import numpy as np

from  __init__ import USEGUI

import pandas
import cv2

if USEGUI:
	import pygame
	from LunCV import Manipulations, Gui
else:
	from LunCV import Manipulations

# Initialize these variables
SIZE_LIST = []
SIZE_LIST_OLD = []
SIZE_LIST_OLD_OLD = []
CENTERS = []
CENTERS_OLD = []
CENTERS_OLD_OLD = []

TEMP0 = 'temp0.csv'
TEMP1 = 'temp1.csv'

CSVFILE = 'experimental_output.csv'
CSVDETECT = 'experimental_detected.csv'

def main():
	'''This is the main function
	'''
	status_flag = True

	# This turns on the debug gui
	if USEGUI:
		status_flag = False
		gui = Gui()
		status_flag = gui.initialize_gui(status_flag)

	# Check to see if our files exist.  If not, create them.
	open(TEMP0, 'w').close()
	open(TEMP1, 'w').close()
	open(CSVFILE, 'w').close()
	open(CSVDETECT, 'w').close()

	# Manually declare that we are at frame 0.
	pos_frame = 0

	# Initialize the CSVFILE by clearing out the old one.
	#with open (CSVFILE, 'wb') as fileout:
		#filewriter = csv.writer(fileout, delimiter=',')
		#row = ('frame #', 'frame contour #', 'X', 'Y', 'Size', 'Contour Speed', 'Contour Area change')
		#filewriter.writerow(row)
	#with open (CSVDETECT, 'wb') as fileout:
		#filewriter = csv.writer(fileout, delimiter=',')
		#row = ('frame #', 'frame contour #', 'X', 'Y', 'Size', 'Contour Speed', 'Contour Area change')
		#filewriter.writerow(row)

	while status_flag:
		if USEGUI:
			gui.frame_number(pos_frame)
		frame, result = runner(pos_frame)
		if USEGUI:
			pos_frame, status_flag = gui.frame_display(pos_frame, frame, result)

		# Increase frame counter.
		pos_frame = pos_frame + 1

	print("Program ended on frame ", str(pos_frame))

def runner(pos_frame):
	'''Runs the script with appropriate manipulation
	'''
	# We need to tell python to use the global declarations from the beginning
	global SIZE_LIST_OLD, CENTERS_OLD, SIZE_LIST_OLD_OLD, CENTERS_OLD_OLD, SIZE_LIST, CENTERS

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

		#SIZE_LIST_OLD_OLD = SIZE_LIST_OLD
		#CENTERS_OLD_OLD = CENTERS_OLD
		#SIZE_LIST_OLD = SIZE_LIST
		#CENTERS_OLD = CENTERS
		SIZE_LIST, CENTERS = lcv.cntsize(contours)

		#use_file = ring_buffer(pos_frame)

		#fit_score, fit_score_2 = bird_velocity(pos_frame, contours)
		#print(fit_score_2)

		bird_correlation(pos_frame)
		bird_dependent_correlation(pos_frame)

		result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
	else:
		frame = []
		result = []

	# This function lets me quit after my test sequence.
	# TODO: remove in final
	if pos_frame > 14999:
		quit()

	return frame, result

def bird_dependent_correlation(pos_frame):
	'''Numpy is used to check frames
	'''

	# We need to tell python to use the global declarations from the beginning
	global CSVDETECT, CSVFILE, TEMP0, TEMP1, CENTERS, SIZE_LIST

	# Thresholds for "good" values of area and speed differences.
	area_threshold = 30
	speed_threshold = 120000

	# The Area Velocity constants are calculated from the calibration relationship
	av_slope = 1.04605
	av_icept = 12.4457


def bird_correlation(pos_frame):
	'''This function checks over the list of contours collected in the CSVFILE,
	and determines what relationship between the contours, if any, have to each
	other.  The number of frames back to search can be modified with the FRAMEHIST
	variable
	'''

	# We need to tell python to use the global declarations from the beginning
	global TEMP0, TEMP1, CSVFILE, CSVDETECT, CENTERS, SIZE_LIST

	# The Area Velocity constants are calculated from the calibration relationship
	av_slope = 1.04605
	av_icept = 12.4457

	# Thresholds for "good" values of area and speed differences.
	area_threshold = 30
	speed_threshold = 120000

	# This is the number of frames we want considered on a single file.  We can go back in time
	# as much as we want (within reason for memory limitations), but this will take longer
	# to calculate. A higher number here will yield better confidence in bird identification.
	last = 3

	for i in range(last, 0, -1):
		if i != 1:
			# Save as name(i) from...the file that used to be name(i-1)
			np.save('/tmp/Frame_minus_{0}'.format(i)+'.npy', np.load('/tmp/Frame_minus_{0}'.format(i-1)+'.npy'))
		else:
			np.save('/tmp/Frame_minus_{0}'.format(i)+'.npy', np.load('/tmp/Frame_current.npy'))

	frame_mat = []
	row = []
	contour_counter = 0
	for i in range(np.size(SIZE_LIST, 0)):
		row = [pos_frame, contour_counter, CENTERS[i][0][0], CENTERS[i][1][0], SIZE_LIST[i]]
		frame_mat.append(row)
		contour_counter += 1

##############################################################

	# Bump up old file in list.
	with open(TEMP0, 'wb') as fileout:
		filewriter = csv.writer(fileout, delimiter=',')
		with open(TEMP1) as filein:
			csvreader = csv.reader(filein)
			for row in csvreader:
				try:
					if int(row[0]) > pos_frame-last:
						filewriter.writerow(row)
				except IndexError:
					pass
			contour_counter = 0
			for i in range(np.size(SIZE_LIST, 0)):
				row = (pos_frame, contour_counter, CENTERS[i][0][0], CENTERS[i][1][0], SIZE_LIST[i])
				filewriter.writerow(row)
				contour_counter += 1

	with open(TEMP0) as filein:
		csvreader = csv.reader(filein, delimiter=',')
		# combines two of the CSV rows together, for each unique permutation (not combination)
		combos = list(itertools.permutations(csvreader, 2))
		# Each combo is a pair of CSV rows.
		# The format is therefore:
		# frame, contour, X, Y, area
		# All seem to require int() to work.
		for pair in combos:
			# if the first part of the pair is from a newer frame
			if int(pair[0][0]) > int(pair[1][0]):
				# This equation is the difference between the predicted value of velocity and the observed.
				# y = m*x+b - sqrt((x1-x2)**2+(y1-y2)**2)
				# This is additionally adjusted for the number of frames away this is.
				score_speed = float((((int(pair[1][0])-int(pair[0][0]))*av_slope*float(pair[1][4])) \
					+ av_icept) - (math.sqrt((float(pair[0][2]) - float(pair[1][2]))**2) + \
						((float(pair[0][3]) - float(pair[1][3]))**2)))

				# Area is simpler.  It is just the difference.
				score_area = (float(pair[0][4]) - float(pair[1][4]))

				outrow = []
				outrow.append(pair[0][0])
				outrow.append(pair[0][1])
				outrow.append(pair[0][2])
				outrow.append(pair[0][3])
				outrow.append(pair[0][4])
				outrow.append(pair[1][0])
				outrow.append(pair[1][1])
				outrow.append(pair[1][2])
				outrow.append(pair[1][3])
				outrow.append(pair[1][4])
				outrow.append(score_speed)
				outrow.append(score_area)
				if abs(score_speed) < speed_threshold:
					if abs(score_area) < area_threshold:
						outrow.append(1)
						with open(CSVDETECT, 'ab') as fileout:
							csvwriter = csv.writer(fileout, delimiter=',')
							csvwriter.writerow(outrow)
					else:
						outrow.append(0)
				else:
					outrow.append(0)

				with open(CSVFILE, 'ab') as fileout:
					csvwriter = csv.writer(fileout, delimiter=',')
					csvwriter.writerow(outrow)

	with open(TEMP0) as filein:
		csvreader = csv.reader(filein, delimiter=',')
		with open(TEMP1, 'wb') as fileout:
			csvwriter = csv.writer(fileout, delimiter=',')
			for row in csvreader:
				csvwriter.writerow(row)

		print("------------------------------", pos_frame, "------------------------------")
	return


#def bird_velocity(pos_frame, contours):
	#'''This function will detect birds based on area and velocity of the contour.
	#The fitness scoring is based on linear relationship between area and velocity.
	#'''

	## We need to tell python to use the global declarations from the beginning
	#global SIZE_LIST_OLD, CENTERS_OLD, SIZE_LIST_OLD_OLD, CENTERS_OLD_OLD, CSVFILE

	## The Area Velocity constants are calculated from the calibration relationship
	#av_slope = 1.04605
	#av_icept = 12.4457

	## These constants are fudge factors for the weight of contour aspects.
	#speed_factor = 0.5
	#area_factor = 0.5

	## Initialize empty lists for the scores
	#top = 0
	#fit_score = []
	#fit_score_2 = []

	#for i in range(np.size(SIZE_LIST, 0)):
		#for j in range(np.size(SIZE_LIST_OLD, 0)):
			#try:
				## This equation is the difference between the predicted value of velocity and the observed.
				## y = m*x+b - sqrt((x1-x2)**2+(y1-y2)**2)
				#score_speed = float(((av_slope*SIZE_LIST_OLD[j])+av_icept) - \
					#(math.sqrt((CENTERS[i][0] - CENTERS_OLD[j][0])**2) + \
						#((CENTERS[i][1] - CENTERS_OLD[j][1])**2)))

				## Area is simpler.  It is just the difference.
				#score_area = (SIZE_LIST[i] - SIZE_LIST_OLD[j])

				## We need to make an equation to test for goodness.
				## a*(1/abs(speed))+b*(1/abs(area))
				##top = ((speed_factor*(1/(abs(score_speed)+1))) + (area_factor*(1/(abs(score_area)+1))))

				#with open(CSVFILE, 'ab') as fileout:
					#filewriter = csv.writer(fileout, delimiter=',')
					#row = (pos_frame, top, CENTERS[i][0][0], CENTERS[i][1][0], \
						#SIZE_LIST[i], score_speed, score_area)
					#filewriter.writerow(row)
				#top += 1


			#except IndexError:
				#pass

	#if SIZE_LIST_OLD_OLD:
		#if fit_score:
			#for i in range(np.size(SIZE_LIST_OLD_OLD, 0)):
				#for j in fit_score[0]:
					#score_speed = float(((av_slope*SIZE_LIST_OLD[j])+av_icept) - \
						#(math.sqrt((CENTERS[i][0] - CENTERS_OLD_OLD[j][0])**2) + \
							#((CENTERS[i][1] - CENTERS_OLD_OLD[j][1])**2)))
					#score_area = (SIZE_LIST_OLD[i] - SIZE_LIST_OLD_OLD[j])

					#fit_score_2.append(pos_frame, CENTERS[i][0][0], CENTERS[i][1][0], \
						#SIZE_LIST[i], score_speed, score_area)


	#return fit_score, fit_score_2

def ring_buffer(pos_frame):
	'''This function provides records the information of the previous frames.
	This must be done via two separate CSV files.  Due to the nature of CSV files,
	it is difficult to insert and remove things like a ring buffer.  So we are using
	a dual file buffer which acts as a ring buffer.  We read from one file while
	writing to another.  The returned use_file tells us which temp file we should
	read from for the most recent info.
	'''
	global TEMP0, TEMP1, SIZE_LIST, CENTERS

	# This is the number of frames we want considered on a single file.  We can go back in time
	# as much as we want (within reason for memory limitations), but this will take longer
	# to calculate. A higher number here will yield better confidence in bird identification.
	last = 3


	if pos_frame % 2: #e.g. odd numbered frames
		with open(TEMP0, 'wb') as fileout:
			filewriter = csv.writer(fileout, delimiter=',')
			with open(TEMP1) as filein:
				csvreader = csv.reader(filein)
				for row in csvreader:
					try:
						if int(row[0]) > pos_frame-last:
							filewriter.writerow(row)
					except IndexError:
						pass
				contour_counter = 0
				for i in range(np.size(SIZE_LIST, 0)):
					row = (pos_frame, contour_counter, CENTERS[i][0][0], CENTERS[i][1][0], SIZE_LIST[i])
					filewriter.writerow(row)
					contour_counter += 1
		use_file = 0

	else: #e.g. even numbered frames
		with open(TEMP1, 'wb') as fileout:
			filewriter = csv.writer(fileout, delimiter=',')
			with open(TEMP0) as filein:
				csvreader = csv.reader(filein)
				for row in csvreader:

					try:
						if int(row[0]) > pos_frame-last:
							filewriter.writerow(row)
					except IndexError:
						pass
				contour_counter = 0
				for i in range(np.size(SIZE_LIST, 0)):
					row = (pos_frame, contour_counter, CENTERS[i][0][0], CENTERS[i][1][0], SIZE_LIST[i])
					filewriter.writerow(row)
					contour_counter += 1
		use_file = 1
	return use_file

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("keyboard task kill")
	finally:
		if USEGUI:
			pygame.quit()
		os.remove(TEMP0)
		os.remove(TEMP1)
