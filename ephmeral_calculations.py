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
					mooninfo = get_moon(datetag).transform_to(AltAz(obstime=datetag,location=site))
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

def bird_ass(tlist, xlist, ylist, rlist, mooninfo):
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
	# Assumption 6: An image of the moon recorded by machine is not subject to the horizon illusion.
	# Assumption 7: Atmospheric turbulence does not impact the image of the birds, and can be ignored.
	
	# Assumptionxxx We are conveniently ignoring the effect on temperature and humidity on low altitude moon...
	# ...observations because it is hard.  Also, it might be below our threshold of caring.  Terrestrial refraction...
	# ...is completely ignored because we will not be measuring birds that low (transit at that angle is not...
	# ...measuring high altitude migration).
	
	# Check for deviation of ellipse predicted by spherical moon and observed ellipse.
	calculate_ideal_ellipse(mooninfo)

	# Total travel time of this bird in these frames
	delt = tlist[2] - tlist[0]

	# Total distance covered by this bird in these frames
	delxy = math.sqr((xlist[2]-xlist[0])**2+(ylist[2]-ylist[0])**2)

	# Averaged direction of this bird
	rotxy = math.atan(((ylist[2]-((ylist[0]+ylist[1])/2))/(xlist[2]-((xlist[0]+xlist[1])/2)))

	# Size of the bird we observed
	relsize = sum(rlist)/3


def calculate_ideal_ellipse(mooninfo):
	'''This function calculates the ideal parameters of the observed ellipse based on the information retrieved
	from astropy.  This can be compared to what is observed.
	'''
	# Distance to the moon in meters
	dist = mooninfo.distance.value
	# Lunar equitorial and polar radii in meters
	# https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html
	eqrd = 1738100
	pord = 1736000
	# Lateral surface area of an elliptical cone
	# L = 1/2 * π * ( a * √ b² + h² + b * √ a² + h² )
	lata = 0.5 * math.pi *(eqrd * math.sqrt(pord**2 + dist**2) + pord * math.sqrt(eqrd**2 + dist**2))
	# Surface area of elliptical cone
	# A = L + π * a * b
	elar = lata + (math.pi * eqrd * pord)
	# Altitude of moon in degrees
	altm = mooninfo.alt.value
	# If the Earth is a perfect sphere and light travels in straight lines. 
	# r = 6371000m, c = 2*pi*r, c = 40030000m, radial distance = c/360 = 111194.4m/deg
	# If we go with the more correct oblate spheroid, it gets more complicated.
	# a = equitorial radius = 6,378,137m
	# b = polar radius = 6,356,752.314245m
	axsa = 6378137
	axsb = 6356752.31424
	# b/a = e = 0.99664718933
	# from WGS84, the first eccentricity squared (e^2) = 0.99330562001
	ecc2 = 0.99330562001
	# Need reduced latitude from our geodetic latitude (θg) from our GPS
	# tan θ = (b/a) tan θg
	latr = math.atan((0.99664718933)*math.tan(mooninfo.location.lat.value))
	# local curvature through the greatarc in the azimutal (φ) direction is:
	# r   =   a (1 - e2 cos2 φ cos2 θ)3/2 / (1 - e2 [1- sin2 φ cos2 θ])1/2
	azim = mooninfo.az.value
	xxxx = math.radians(math.cos(azim)**2)
	yyyy = math.radians(math.cos(latr)**2)
	zzzz = math.radians(math.sin(azim)**2)
	radi = (axsa*(1-(ecc2*xxxx*yyyy))**(3/2))/((1-(ecc2*(1-(zzzz*yyyy))))**(1/2))
	

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
