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
#import time
#import numpy as np

#import ephem
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

def main(the_file):
	'''main function
	'''

	pos_frame = 0
	file_datetime = str(the_file)
	file_datetime = (file_datetime.split('/')[-1].split('outA.'))[0]

	lcv = Manipulations.Manipulations()
	rbf = RingBuffer.RingBufferClass()

	#for i in range(0, LAST):
		#aaa.append(i)
		#ccc = 'cont_{0}'.format(i)
		#bbb.append(ccc)
	#var_dict = {key:value for key, value in zip(aaa, bbb)}

	#while pos_frame < 84:
	while True:
		cap = cv2.VideoCapture(the_file)
		#cap = cv2.VideoCapture('/scratch/whoneyc/1535181028stabilized.mp4')
		#cap = cv2.VideoCapture('/home/wes/Pictures/Demobird/videoout.mp4')
		cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
		ret, frame = cap.read()

		##Info for debugging
		#for i in range(LAST, 1, -1):
			#if i <= pos_frame:
				#aaa = '/scratch/whoneyc/contours_minus_cont_{0}'.format(i-2)+'.p'
				#bbb = '/scratch/whoneyc/contours_minus_cont_{0}'.format(i-1)+'.p'
				#os.rename(aaa, bbb)

		# bird in demo images appears at img 70
		# So first we run this for loop to establish the background
		if ret:
			#print(pos_frame)
			if True:#placeholder for another switch
				#Necessary cleanup of rbf class
				rbf.re_init(pos_frame, LAST)

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

				# Subtract Background
				img = lcv.subtract_background(frame)

				# Remove Halo Noise
				img = lcv.halo_noise(ellipse, img)

				# Get Contours Again
				contours = lcv.cv_contour(img, 0, 255)

				if contours:
					rbf.get_centers(pos_frame, contours)

				##Info for debugging
				#with open('/scratch/whoneyc/contours_minus_cont_0.p', 'wb') as fff:
					#pickle.dump(contours, fff)

				# Dirty conversion to binary b/w
				img[img > 0] = 1

				# Deal with ringbuffer on LAST frames
				rbf.ringbuffer_cycle(pos_frame, img, LAST)
				img = rbf.ringbuffer_process(pos_frame, img, LAST)
				goodlist = rbf.centers_local(pos_frame, img)
				if goodlist.size > 0 and goodlist.size < 300:
					lrs = rbf.longer_range(pos_frame, img, goodlist)
					# Screenshot
					if lrs:
						cv2.imwrite('/scratch/whoneyc/original_%09d.png' % pos_frame, frame)
						frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
						added_image = cv2.addWeighted(frame, 0.5, img, 0.5, 0)
						cv2.imwrite('/scratch/whoneyc/contours_%09d.png' % pos_frame, added_image)

				#cv2.imshow('image', img)
				cv2.waitKey(1)

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
	else:
		return arg

def get_parser():
	'''Get parser object for script processor.py
	'''
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	parser = ArgumentParser(description=__doc__,
							formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument("-f", "--file",
						dest="filename",
						required=True,
						type=lambda x: is_valid_file(parser, x),
						help="write report to FILE",
						metavar="FILE")
	#parser.add_argument("-n",
						#dest="n",
						#default=10,
						#type=int,
						#help="how many lines get printed")
	#parser.add_argument("-q", "--quiet",
						#action="store_false",
						#dest="verbose",
						#default=True,
						#help="don't print status messages to stdout")
	return parser


#def ephreport(pos_frame):
	#'''Uses the ephem class to get values for moon locations based on time.
	#Input the latitude (N), longitude (E), and observation time (UTC)
	#'''

	#gatech = ephem.Observer()
	## Norman, OK
	#gatech.lat = '35.2226'
	#gatech.lon = '-97.4395'
	## Spotted at 1:33 AM on Sept. 25th
	## In UTC +5

	## Start time of video in Unix time (UTC)
	#starttime = 1537857180

	## Account for time of each frame.
	#frametime = starttime + int(pos_frame/25)

	## Assign timestamp in string format
	#gatech.date = datetime.utcfromtimestamp(frametime).strftime('%Y/%m/%d %H:%M:%S')

	##resutc = ("At UTC time of " + str(gatech.date))
	##resobs = ("From Norman, OK (" + str(gatech.lat) + "N, " + str(gatech.lon) + "E)")

	## Retrieve Positional information from the time we entered.
	#position = ephem.Moon(gatech)
	#azz = str(position.az).split(':')
	#alt = str(position.alt).split(':')

	#azzsec = []
	#altsec = []
	#for i in azz:
		#azzsec.append(float(i))
	#for i in alt:
		#altsec.append(float(i))

	#altdeg = altsec[0]+0.01666667*altsec[1]+0.00027778*altsec[2]
	#azzdeg = azzsec[0]+0.01666667*azzsec[1]+0.00027778*azzsec[2]

	##TODO add conics


	#slope = sum(slopelist)/len(slopelist)
	#intercept = sum(interlist)/len(slopelist)
	#print(slope, intercept)






	##resalt = ("We are looking up by " + str(altdeg) + " degrees")
	##resazz = ("We are looking " + str(azzdeg) + " East of North")
	##respth = ("The bird is moving along a roughly linear path of the form")
	##respt2 = ("         y = " + str(slope) + " + " + str(intercept))
	##reswut = ("           Why was this bird going NNE?")

	##cv2.rectangle(img,(0,0),(1920,150),(0,0,0),-1)


	##cv2.putText(img, resalt ,(10,200), font, 2,(255,255,255),2,cv2.LINE_AA)
	##cv2.putText(img, resazz ,(10,300), font, 2,(255,255,255),2,cv2.LINE_AA)
	##cv2.putText(img, respth ,(10,500), font, 2,(255,255,255),2,cv2.LINE_AA)
	##cv2.putText(img, respt2 ,(10,600), font, 2,(255,255,255),2,cv2.LINE_AA)
	##cv2.putText(img, reswut ,(10,800), font, 2,(255,255,255),2,cv2.LINE_AA)
	##cv2.imwrite('ephem_12.png', img)
	##cv2.imshow('image',img)
	##cv2.waitKey(0)


if __name__ == '__main__':
	args = get_parser().parse_args()
	print(args.filename)
	try:
		main(args.filename)
	except KeyboardInterrupt:
		print("keyboard task kill")
	finally:
		cv2.destroyAllWindows()
		## Wipe the old numpy junk from scratch directory.
		#try:
			#files = os.listdir('/scratch/whoneyc/')
			#for file in files:
				#if file.endswith(".npy"):
					#os.remove(os.path.join('/scratch/whoneyc/',file))
			#os.remove('/scratch/whoneyc/Frame_current.npy')
		#except FileNotFoundError:
			#pass
