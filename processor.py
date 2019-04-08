#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi.  If you choose to run this
on the RasPi, make sure that USEGUI in ./__init__.py is False.
'''

from __future__ import print_function

#import argparse
#import csv
#from datetime import datetime
#import itertools
#import math
import os
#import pickle
import sys
#import time

#import ephem
#import numpy as np
#from scipy import stats

import cv2
from LunCV import Manipulations, RingBuffer

#kalman = cv2.KalmanFilter(2, 1, 0)
#state = 0.1 * np.random.randn(2, 1)
#kalman.transitionMatrix = np.array([[1., 1.], [0., 1.]])
#kalman.measurementMatrix = 1. * np.ones((1, 2))
#kalman.processNoiseCov = 1e-5 * np.eye(2)
#kalman.measurementNoiseCov = 1e-1 * np.ones((1, 1))
#kalman.errorCovPost = 1. * np.ones((2, 2))
#kalman.statePost = 0.1 * np.random.randn(2, 1)

LAST = 5
# Lazy solution to a start-at-zero problem.
LAST = LAST + 2

def main(the_file, gui, pos_frame, procpath):
	'''main function
	'''

	file_datetime = str(the_file)
	file_datetime = (file_datetime.split('/')[-1].split('outA.'))[0]

	lcv = Manipulations.Manipulations()
	rbf = RingBuffer.RingBufferClass(LAST, procpath)

	#while True:
	while pos_frame < 1000:
		rbf.set_pos_frame(pos_frame)
		print(pos_frame)
		cap = cv2.VideoCapture(the_file)
		#cap = cv2.VideoCapture('/scratch/whoneyc/1535181028stabilized.mp4')
		#cap = cv2.VideoCapture('/home/wes/Pictures/Demobird/videoout.mp4')
		cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
		ret, frame = cap.read()

		if ret:
			#Necessary cleanup of rbf class
			rbf.re_init(LAST)

			# Make image gray
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			# Blur Image
			frame = cv2.GaussianBlur(frame, (5, 5), 0)

			# Get thresholds
			lower_thresh, upper_thresh = lcv.magic_thresh(frame)

			# Get contours
			contours = lcv.cv_contour(frame, lower_thresh, upper_thresh)

			# Center Moon
			ellipse, frame = lcv.center_moon(frame, contours)

			with open(procpath + '/outputellipse.csv', 'a') as fff:
				outstring = str(pos_frame) + ',' + str(ellipse[0][0]) + ',' + str(ellipse[0][1])\
					+ ',' + str(ellipse[1][0]) + ',' + str(ellipse[1][1]) + ',' + str(ellipse[2]) + '\n'
				fff.write(outstring)

			# Subtract Background
			img = lcv.subtract_background(frame)

			# Remove Halo Noise
			img = lcv.halo_noise(ellipse, img)

			# Get Contours Again
			contours = lcv.cv_contour(img, 0, 255)

			if contours:
				rbf.get_centers(contours)

			##Info for debugging
			#with open('/scratch/whoneyc/contours_minus_cont_0.p', 'wb') as fff:
				#pickle.dump(contours, fff)

			# Dirty conversion to binary b/w
			img[img > 0] = 1

			# Deal with ringbuffer on LAST frames
			rbf.ringbuffer_cycle(img, LAST)
			img = rbf.ringbuffer_process(img, LAST)
			goodlist = rbf.pull_list()
			# Number of contours limiter
			if goodlist.size > 0 and goodlist.size < 300:
				img = rbf.bird_range(img, frame, goodlist)

			if gui:
				#img[img < 0] = 255
				cv2.imshow('image', img)

			cv2.waitKey(1)

		else:
			break

		pos_frame += 1

def is_valid_file(parser, arg):
	'''
	Check if arg is a valid file that already exists on the file system.

	Parameters
	----------
	parser : argparse object
	arg : str

	Returns
	-------
	arg
	'''
	arg = os.path.abspath(arg)
	if not os.path.exists(arg):
		parser.error("The file %s does not exist!" % arg)
		sys.exit(1)
	else:
		return arg

def get_parser():
	'''Get parser object for script processor.py
	'''
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument("-f", "--file", dest="filename", required=True,\
		type=lambda x: is_valid_file(parser, x), help="write report to FILE", metavar="FILE")
	parser.add_argument("-g", "--gui", dest="gui", action="store_true", default=False,\
		help="show the slides as you are processing them.")
	parser.add_argument("-n", "--nthframe", dest="pos_frame", type=int, default=0,\
		help="set starting frame number; defaults 0\n *NOTE: This changes the basis set/early results!")
	#parser.add_argument("-q", "--quiet",
						#action="store_false",
						#dest="verbose",
						#default=True,
						#help="don't print status messages to stdout")
	return parser

def read_proc_number():
	'''Look for deleteme file.
	If it exists, parse it for the number we need
	Else, die
	'''
	arg = os.path.abspath("./deleteme")
	if not os.path.exists(arg):
		print("the deleteme file does not exist")
		sys.exit(1)
	else:
		with open("./deleteme", 'r') as fff:
			procpath = fff.read()
			return procpath


if __name__ == '__main__':
	ARGS = get_parser().parse_args()
	print(ARGS.filename)
	try:
		main(ARGS.filename, ARGS.gui, ARGS.pos_frame, read_proc_number())
	except KeyboardInterrupt:
		print("keyboard task kill")
	finally:
		cv2.destroyAllWindows()
		try:
			os.remove("./deleteme")
		except FileNotFoundError:
			pass
