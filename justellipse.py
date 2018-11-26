#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi.  If you choose to run this
on the RasPi, make sure that USEGUI in ./__init__.py is False.
'''

from __future__ import print_function

import os

import cv2
from LunCV import Manipulations

LAST = 5
# Lazy solution to a start-at-zero problem.
LAST = LAST + 2

def main(the_file, pos_frame):
	'''main function
	'''

	file_datetime = str(the_file)
	file_datetime = (file_datetime.split('/')[-1].split('outA.'))[0]

	lcv = Manipulations.Manipulations()

	while True:
		print(pos_frame)
		cap = cv2.VideoCapture(the_file)

		cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
		ret, frame = cap.read()

		if ret:

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

			with open('./outputellipse.csv', 'a') as fff:
				outstring = str(pos_frame) + ',' + str(ellipse[0][0]) + ',' + str(ellipse[0][1])\
					+ ',' + str(ellipse[1][0]) + ',' + str(ellipse[1][1]) + ',' + str(ellipse[2]) + '\n'
				fff.write(outstring)

			cv2.waitKey(1)

		else:
			print("end of the line")
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
	else:
		return arg

def get_parser():
	'''Get parser object for script processor.py
	'''
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument("-f", "--file", dest="filename", required=True,\
		type=lambda x: is_valid_file(parser, x), help="write report to FILE", metavar="FILE")
	parser.add_argument("-n", "--nthframe", dest="pos_frame", type=int, default=0,\
		help="set the starting frame number; defaults to 0.\n *NOTE: This changes the basis set/early results!")
	#parser.add_argument("-q", "--quiet",
						#action="store_false",
						#dest="verbose",
						#default=True,
						#help="don't print status messages to stdout")
	return parser

if __name__ == '__main__':
	ARGS = get_parser().parse_args()
	print(ARGS.filename)
	try:
		with open('./outputellipse.csv', 'w') as fff:
				fff.write('')
		main(ARGS.filename, ARGS.pos_frame)
	except KeyboardInterrupt:
		print("keyboard task kill")
	finally:
		cv2.destroyAllWindows()
		quit()

