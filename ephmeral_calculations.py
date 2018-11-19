#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi.  If you choose to run this
on the RasPi, make sure that USEGUI in ./__init__.py is False.
'''

from __future__ import print_function

#import csv
from datetime import datetime
#import itertools
import math
import os
#import pickle
import re
#import time
#import numpy as np

import astropy.units as units
from astropy.time import Time
from astropy.coordinates import get_moon, EarthLocation, AltAz
from scipy import stats

import cv2
#from LunCV import Manipulations, RingBuffer

def main(filein, fileout, forced_date, utcoffset, lat, lon, elev):
	'''main function
	'''

	# Get timestamp from file name
	# Takes the forced date input by the user
	if forced_date:
		unixdate = forced_date
	# Gets a string of 10 consecutive numbers from the input string
	else:
		unixdate = re.findall('\d{10}', filein)

	# Correctly type input values and add units
	utcoffset = int(utcoffset)*units.hour
	site = EarthLocation(lat=int(lat)*units.deg, lon=int(lon)*units.deg, height=int(elev)*units.m)

	datetag = ''
	frametime = ''
	with open(filein, "r") as fffin:
		reader = csv.reader(fffin, delimiter=',')
		for i, row in enumerate(reader):
			tlist = []
			xlist = []
			ylist = []
			rlist = []
			if i % 4 == 0:
				# Skip if we already know the moon location for this time point
				if frametime != row[0]:
					frametime = row[0]
					# Convert the unixtime of the frame to a format readible by astropy
					ucorrtime = unixdate + frametime
					datetag = Time(datetime.utcfromtimestamp(ucorrtime).strftime('%Y-%m-%d %H:%M:%S.%f')) - utcoffset
					get_moon(datetag).transform_to(AltAz(obstime=datetag,location=site))
				else:
					pass
			elif i % 4 in (1, 2):
				tlist.append(row[0])
				xlist.append(row[1])
				ylist.append(row[2])
				rlist.append(row[3])
			else:
				tlist.append(row[0])
				xlist.append(row[1])
				ylist.append(row[2])
				rlist.append(row[3])

				
				with open(fileout, "a") as fffout:
					fffout.write(frametime + ',' + ucorrtime + ',')

	# Initialize our output file.
	with open(fileout, "w") as fffout:
		fffout.write("frame, " + "timestamp, " + "realtime\n")
	
	return

def bird_ass(tlist, xlist, ylist, rlist):
	'''Math is done on the observed bird
	
	Bird final location is the last in the list, so the coordinates are (xlist[2], ylist[2])
	'''
	# Assumption 1: The max bird flight ceiling we observe is 10,000ft(3048m) according to the book.
	# Assumption 2: All birds are isochoric and spherical.
	# Assumption 3: The pixel resolution of the camera is such that any size changes are considered errors.
	# It follows that a good telescope can see a bird an infinite distance away in good conditions.
	# This set of assumptions (which are mutable) states that a bird of 1px size is the ceiling height away.
	birdceil = 3048

	# Assumption 4: All birds travel in straight lines which cut a plane through our viewing cone orthogonal to...
	# ...the antipodal axis from zenith to nadir.  We ignore the true horizon for birds relatively close to us.
	# Assumption 5: The moon is a constant distance away from the earth during this transit period.
	# Assumption 6: The observer of the moon is not beholden to atmospheric or gravitational lensing.
	

	# Total travel time of this bird in these frames
	delt = tlist[2] - tlist[0]

	# Total distance covered by this bird in these frames
	delxy = math.sqr((xlist[2]-xlist[0])**2+(ylist[2]-ylist[0])**2)

	# Averaged direction of this bird
	rotxy = math.atan(((ylist[2]-((ylist[0]+ylist[1])/2))/(xlist[2]-((xlist[0]+xlist[1])/2)))

	# Size of the bird we observed
	relsize = sum(rlist)/3

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

def is_valid_unixtime(parser, arg):
	'''Check if the unix string entered is a valid 10-digit timestamp.
	If you are using this after 2038, I apologize for my lazy coding
	'''
	arglen = len(str(arg))
	if arglen != 10:
		parser.error("The date you entered (%s) must be a 10-digit unix time stamp!" % arg)
	else:
		return arg

def outfile_exists(parser, arg):
	arg = os.path.abspath(arg)
	if os.path.exists(arg):
		answer = ''
		print("The output file you selected (%s) already exists." % arg)
		while not answer in {'y', 'n'}:
			answer = input("Overwrite? (y/n) ").lower()
			if answer == 'n':
				parser.error("Try again with a new output file path")
			elif answer == 'y':
				return arg
	else:
		return arg
		

def get_parser():
	'''Get parser object for script processor.py
	'''
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument("-i", "--input", dest="filein", required=True,\
		type=lambda x: is_valid_file(parser, x), help="input csv file with LunAero formatting", metavar="INFILE")
	parser.add_argument("-o", "--output", dest="fileout", required=True,\
		type=lambda x: outfile_exists(parser, x), help="output file name", metavar="OUTFILE")
	parser.add_argument("-D", "--date", dest="forced_date", required=False,\
		type=lambda x: is_valid_unixtime(parser, x), help="Set date of video start with 10-digit unix timestamp", metavar="UNIXTIME")
	parser.add_argument("-u", "--utc", dest="utcoffset", required=True,\
		type=str, help="UTC offset. USE QUOTES. Ex: \'-5\'", metavar="STRING")
	parser.add_argument("-l", "--lat", dest="lat", required=True,\
		type=str, help="Latitude in degrees North of equator, USE QUOTES. Ex: \'35.221\'", metavar="STRING")
	parser.add_argument("-L", "--Lon", dest="lon", required=True,\
		type=str, help="Longitude in degrees East of Greenwich.  USE QUOTES. Ex: \'-97.446\'", metavar="STRING")
	parser.add_argument("-e", "--elevation", dest="elev", required=True,\
		type=str, help="Elevation above sea-level in meters  USE QUOTES. Ex: \'356.9\'", metavar="STRING")
	#parser.add_argument("-m", "--mode", dest="mode", required=True, type=int,\
		#help="processing mode: 0=none, 1=simple_regression, 2=local_linear, 3=longer_range")
	#parser.add_argument("-g", "--gui", dest="gui", action="store_true", default=False,\
		#help="show the slides as you are processing them.")
	#parser.add_argument("-n", "--nthframe", dest="pos_frame", type=int, default=0,\
		#help="set the starting frame number; defaults to 0.\n *NOTE: This changes the basis set/early results!")
	#parser.add_argument("-q", "--quiet",
						#action="store_false",
						#dest="verbose",
						#default=True,
						#help="don't print status messages to stdout")
	return parser

if __name__ == '__main__':
	ARGS = get_parser().parse_args()
	print(ARGS.filein)
	try:
		main(ARGS.filein, ARGS.fileout, ARGS.forced_date, ARGS.utcoffset, ARGS.lat, ARGS.lon, ARGS.elev)
	except KeyboardInterrupt:
		print("keyboard task kill")
	finally:
		quit()
