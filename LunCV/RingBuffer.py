#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

"""This is a buffering class used for the LunAero prototype processor.  It does most of the
heavy lifting in the calculation of bird locations.
"""

import gc
import os

import numpy as np

import cv2

class RingBufferClass():
	"""This is a buffering class used for the LunAero prototype processor."""

	# Reserved memory spaces for ring buffer lists
	aaa = []
	bbb = []
	# Reserved memory spaces for information about contour details
	tim = []
	rad = []
	xxx = []
	yyy = []
	# Reserved memory space for our working directory path.
	procpath = []
	# This is a local framecounter.
	pfs = 0

	def __init__(self, procpath, radr=10, rada=0.0, sper=2, spea=2e-5, angr=2e-2, anga=2e-5, \
		fill=(255, 0, 63), width=1, last=5):
		"""
		Initialize the class with the following commands.  It may be called with
		optional parameters.  Tolerances factors: Values are the rel. tolerance and abs. tolerance of
		variable.  Relative tolerance is the least significant digit.  Absolute tolerance is the
		threshold for giving up.  Numpy is weird on this.  The numpy version
			absolute(a - b) <= (atol + rtol * absolute(b))
		is not reversible, but that shouldn't matter for our stuff because of the implicit ordering
		here.

		:param procpath: This is a string that represents the absolute path of the working
			directory for our process (where the video lives).
		:param radr: relative tolerance (least significant digit) of radius closeness checker.
		:param rada: absolute tolerance of radius closensss checker.
		:param sper: relative tolerance (least significant digit) of speed closeness checker.
		:param spea: absolute tolerance of speed closeness checker. Should not be zero, because a zero
			speed is possible.
		:param angr: relative tolerance (least significant digit) of angle closeness checker.
		:param anga: absolute tolerance of angle closeness checker.  Should not be zero, because a zero
			angle is possible.
		:param fill: Fill color for line.  This should be an RGB tuple.  Default is a lovely shade
			of lavender.
		:param width: Width of the line for the box.  Default is 1.
		:param last: This is an int that tells the class how far back in frame-time to look.
			Default value is 5.
		"""
		# Create class values from init options.
		self.radr = radr
		self.rada = rada
		self.sper = sper
		self.spea = spea
		self.angr = angr
		self.anga = anga
		self.fill = fill
		self.width = width
		self.last = last + 2
		self.procpath = procpath
		# Numpy, quit using scientific notation, its painful
		np.set_printoptions(suppress=True)
		# Create a directory at our path target and the subdirectories.
		os.mkdir(self.procpath)
		os.mkdir(self.procpath + '/orig_w_birds')
		os.mkdir(self.procpath + '/mixed_contours')
		# Create a new empty file for our csv output
		fff = self.procpath + '/longer_range_output.csv'
		with open(fff, 'w') as fff:
			fff.write('')
		# If we are not starting at frame zero, fudge some empty frames in there
		if self.pfs > 0:
			emptyslug = np.zeros((1080, 1920), dtype='uint8')
			for i in range(0, self.last):
				aaa = procpath + '/Frame_minus_{0}'.format(i)+'.npy'
				np.save(aaa, emptyslug)
		return

	def re_init(self):
		"""This function is called at the beginning of a main loop to
		clean up some of the leftovers from a previous frame
		If we don't call this, the ringbuffer may still have information stored from the previous
		run, and this can mess up our results.
		aka: magic function, do not touch.
		"""
		self.aaa = []
		self.bbb = []
		tempt = self.tim
		tempr = self.rad
		tempx = self.xxx
		tempy = self.yyy
		self.tim = []
		self.rad = []
		self.xxx = []
		self.yyy = []
		for i in enumerate(tempt):
			if tempt[i[0]] >= (self.pfs - self.last):
				self.tim.append(tempt[i[0]])
				self.xxx.append(tempx[i[0]])
				self.yyy.append(tempy[i[0]])
				self.rad.append(tempr[i[0]])

	def ringbuffer_cycle(self, img):
		"""Saves the contours from the image in a ring buffer.
		"""
		filename = self.procpath + '/Frame_minus_0.npy'
		np.save(filename, img)

		for i in range(self.last, 0, -1):
			if self.pfs == 0:
				continue
			elif (self.pfs - i + 1) >= 0:
				try:
					# Save as name(i) from...the file that used to be name(i-1)
					self.aaa = self.procpath + '/Frame_minus_{0}'.format(i-2)+'.npy'
					self.bbb = self.procpath + '/Frame_minus_{0}'.format(i-1)+'.npy'
					oldone = np.load(self.aaa)
					np.save(self.bbb, oldone)
				except FileNotFoundError:
					pass
		return

	def ringbuffer_process(self, img):
		"""Access the existing ringbuffer to get information about the last frames.
		Perform actions within.
		"""
		self.bbb = np.load(self.procpath + '/Frame_minus_0.npy')
		if self.pfs == 0:
			pass
		elif self.pfs >= self.last:
			for i in range(self.last, 1, -1):
				try:
					self.aaa = self.procpath + '/Frame_minus_{0}'.format(i-2)+'.npy'
					self.aaa = np.load(self.aaa)
					self.bbb = np.add(self.aaa, self.bbb)
					np.save(self.procpath + '/Frame_minus_0.npy', self.bbb)
				except TypeError:
					print("bailing on error")
			self.bbb = np.load(self.procpath + '/Frame_minus_0.npy')
			self.bbb[self.bbb > 1] = 0
			self.bbb[self.bbb == 1] = 255
			np.save(self.procpath + '/Frame_mixed.npy', self.bbb)

			img = np.load(self.procpath + '/Frame_mixed.npy')

			img[img > 0] = 255

			if self.tim:
				img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		return img

	def get_centers(self, contours):
		"""Extract information from the contours including the x,y of the center, radius, and
		frame.  Exclude contours with perimeters which are very large or very small.
		"""
		cnt = contours[0]
		for cnt in contours:
			perimeter = cv2.arcLength(cnt, True)
			if perimeter > 8 and perimeter < 200:
				(xpos, ypos), radius = cv2.minEnclosingCircle(cnt)
				self.tim.append(self.pfs)
				self.rad.append(radius)
				self.xxx.append(xpos)
				self.yyy.append(ypos)
		return

	def pull_list(self):
		"""Repackages the list elements after the ring buffer operates to create a list with
		the correct formatting.
		"""
		goodlist = np.column_stack((self.tim, self.xxx, self.yyy, self.rad))
		return goodlist

	def bird_range(self, img, frame, gdl):
		"""An adaptable range processor, takes values of each frame, then runs those values vs.
		previous frame values
		"""
		# Process Numpy Array with floats in a format:
		gdl = np.reshape(gdl, (-1, 4))
		gdl = np.unique(gdl, axis=0)
		# Run the gauntlet!
		fltx, flty, fltz = self.gauntlet(gdl)

		# TODO make tunable isclose value variables

		##One list to rule them all
		if np.size(fltx, 0) == 0 and np.size(flty, 0) == 0 and np.size(fltz, 0) == 0:
			gc.collect()
			return img

		#TEST
		print("x: ", fltx.shape, "\ny: ", flty.shape, "\nz: ", fltz.shape, "\n")

		fourlist = np.vstack((fltx, flty, fltz))
		del fltx, flty, fltz

		img = self.output_points(fourlist, img)

		#TEST
		print("fourlist\n", fourlist)

		# Save contour information to file
		with open(self.procpath + '/longer_range_output.csv', 'ab') as fff:
			np.savetxt(fff, fourlist, delimiter=",", fmt='%0.2f')

		# Save original image which is believed to contain birds
		cv2.imwrite(self.procpath + '/orig_w_birds/original_%09d.png' % self.pfs, frame)

		# Overlay the boxed birds to the original image
		frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
		added_image = cv2.addWeighted(frame, 0.5, img, 0.5, 0)

		# Save  mixed image to file
		cv2.imwrite(self.procpath + '/mixed_contours/contours_%09d.png' % self.pfs, added_image)

		#Cleanup what we have left to free memory
		del fourlist
		gc.collect()

		return img

	def output_points(self, infile, img):
		"""
		This function converts the input array from the bird finder to points which can be
		used to draw on the bitmap.
		"""
		# We just want the XY points, but we still want them grouped up by what they match with.
		# Our current row is shaped like
		# T1, X1, Y1, D1,
		# T2, X2, Y2, D2,
		# V1, V2, R12,
		# T3, X3, Y3, D3,
		# T4, X4, Y4, D4,
		# V3, V4, R34
		mask = np.array([[\
			False, True, True, False, \
			False, True, True, False,\
			False, False, False, \
			False, True, True, False, \
			False, True, True, False, \
			False, False, False]])
		points = np.reshape(infile[np.all(mask*[infile], axis=0)], (-1, 4, 2))
		points = np.unique(points, axis=0)
		points = np.divide(points, 10)
		points = points.astype('int')
		# Each grouping of points should be boxed
		for ppp in points[:]:
			img = self.draw_rotated_box(img, ppp)

		#TEST
		print("points\n", points)

		return img

	def gauntlet(self, gdl):
		"""
		The gauntlet is a collection of the major tests that our data goes through to be considered
		valid.  See the infomation for individually called self functions for more info.  Uses a
		dictionary referencing scheme to quickly cycle through the lists of lists.

		:param gdl: The input data set.  This should be a sanitized 'goodlist'.
			Must be a Numpy array with shape [:, 3].

		:returns: np.ndarray np.ndarray np.ndarray
			-fltx - Paired list of good values from frame n and n-1.  Has shape [:, 22]
			-flty - Paired list of good values from frame n-1 and n-2.  Has shape [:, 22]
			-fltz - Paired list of good values from frame n-2 and n-3.  Has shape [:, 22]
		"""
		# Local constants
		radii_minimum = 2
		# Multiply rows to increase accuracy
		# Make an int only array (multiplied by 10 to include significant digit decimal) for x,y
		# locaions.  Remember the 10x!
		gdl = (gdl * np.array([1, 10, 10, 10000], np.newaxis)).astype(dtype=int)
		# Remove rows with radii less than a certain size
		gdl = gdl[np.greater_equal(gdl[:, 3], radii_minimum), :]
		# List of Arays
		ins = {"gdl0":np.empty((0, 9), int), "gdl1":np.empty((0, 9), int), \
			"gdl2":np.empty((0, 9), int), "gdl3":np.empty((0, 9), int)}
		outs = {"fltx":np.empty((0, 9), int), "flty":np.empty((0, 9), int), \
			"fltz":np.empty((0, 9), int)}
		inslist = ["gdl0", "gdl1", "gdl2", "gdl3"]
		outslist = ["fltx", "flty", "fltz"]
		for i in range(0, 4):
			ins[inslist[i]] = gdl[np.equal(gdl[:, 0], self.pfs-i), :]
		for i in range(0, 3):
			# Process each sequential image for distance
			outs[outslist[i]] = self.stackdistance(ins[inslist[i]], ins[inslist[i+1]])
			# Cleanup to prevent overeating memory
			outs[outslist[i]] = self.getspeed(outs[outslist[i]])
			# Get direction for each item on the list
			outs[outslist[i]] = self.getdir(outs[outslist[i]])
			# Run a size test.  The radius should be relatively constant.
			outs[outslist[i]] = outs[outslist[i]][np.isclose(outs[outslist[i]][:, 3], \
				outs[outslist[i]][:, 7], rtol=self.radr, atol=self.rada)]
		# Compare the generated lists (second order)
		fltn = self.combineperms(outs["fltx"], outs["flty"])
		outs["flty"] = self.combineperms(outs["flty"], outs["fltz"])
		outs["fltz"] = self.combineperms(outs["fltx"], outs["fltz"])
		outs["fltx"] = fltn
		for i in range(0, 3):
			#If we have empty lists, we need to make them empty with the right size
			outs[outslist[i]] = self.gapinghole(outs[outslist[i]])
			# Test distance/direction
			outs[outslist[i]] = self.distdirtest(outs[outslist[i]])
			# Only keep continuous lines
			outs[outslist[i]] = self.linear_jump(outs[outslist[i]])
			# Check that we are not bouncing around the same craters
			outs[outslist[i]] = self.reversal_check(outs[outslist[i]])
			# Sync up the velocity values
			outs[outslist[i]] = self.match_speed(outs[outslist[i]])
		return outs["fltx"], outs["flty"], outs["fltz"]

	def stackdistance(self, in1, in2, smin=2, smax=200):
		"""
		This function creates a single side-by-side permutation array from two input
		arrays (combineperms), then tests the distance the tracked objects have travelled in
		the frame.  This test adds an additional column to the end of the array. If the arrays are
		empty, it just outputs an empty [0, 8] array.

		:param in1: Numpy array input 1, should have size [:, 3]
		:param in2: Numpy array input 2, should have size [:, 3]
		:param smin: Minimum object speed in pixels/frame
		:param smax: Maximum object speed in pixels/frame

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 8]
		"""
		# Start empty Numpy array
		out = np.empty((0, 8), int)
		# Kill early check
		if np.size(in1, 0) & np.size(in2, 0):
			# Make the arrays side by side row permutations
			# We column_stack in1 which was repeated and in2 which was tiled
			out = self.combineperms(in1, in2)
			# Distance formula for each item, resets int mod
			out = np.column_stack((out, np.divide(np.sqrt(np.square(np.subtract(\
				out[:, 1], out[:, 5])) + np.square(np.subtract(out[:, 2], out[:, 6]))), 10)))
			# The value at dist passes a test, we treat the row as true, else false row.
			# This is broadcast back to our out
			out = out[np.where((out[:, 8]/10 > smin) & (out[:, 8]/10 < smax), True, False)]
		return out

	def getspeed(self, inout):
		"""
		Gets the speed in pixels/frameduration for the contours in a list which appear to be
		moving.

		:param inout: Numpy array input.  Must have size [:, 8]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 8]
		"""
		if np.size(inout, 0) == 0:
			return inout
		inout = np.column_stack((inout, np.divide(inout[:, 8], np.abs(np.subtract(inout[:, 0], \
			inout[:, 4])))))
		return inout

	def getdir(self, inout):
		"""
		Determines the direction in degrees North of East (atan2 type) a moving contour appears
		to be moving between frames.

		:param inout: Numpy array input.  Must have size [:, 8]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 8]
		"""
		if np.size(inout, 0) == 0:
			return inout
		inout = np.column_stack((inout, np.arctan2(np.subtract(inout[:, 2], inout[:, 6]), \
			np.subtract(inout[:, 1], inout[:, 5]))*(180/np.pi)))
		return inout

	def combineperms(self, in1, in2):
		"""Combines numpy arrays in a row-by-row type of permutation.  Put two arrays in,
		and pop out just one!
		"""
		# Combine columns using the repeat and tile method
		out = np.column_stack((np.repeat(in1, np.size(in2, 0), axis=0), \
			np.tile(in2, (np.size(in1, 0), 1))))
		return out

	def distdirtest(self, inout):
		"""
		Tests for distance and direction without bounds for compared list items.
		Keeps good ones.

		:param inout: Numpy array input.  Must have size [:, 22]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 22]
		"""
		#if np.size(inout, axis=1) < 20:
			#return inout
		# Test distance
		inout = inout[np.isclose(inout[:, 8], inout[:, 19], rtol=self.sper, atol=self.spea)]
		# Test direction
		inout = inout[np.isclose(inout[:, 10], inout[:, 21], rtol=self.angr, atol=self.anga)]
		return inout

	def gapinghole(self, inout):
		"""
		If it is empty, make it empty with the right size

		:param inout: Numpy array input.  Must have size [:, 22]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 22]
		"""
		if np.size(inout, 0) == 0:
			inout = np.empty((0, 22), int)
		return inout

	def linear_jump(self, inout):
		"""Tests if the jump between the newly conjoined list matches up.

		:param inout: Numpy array input.  Must have size [:, 22]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 22]
		"""
		inout = inout[np.where(inout[:, 4] == inout[:, 11])]
		inout = inout[np.where(inout[:, 5] == inout[:, 12])]
		inout = inout[np.where(inout[:, 6] == inout[:, 13])]
		return inout

	def reversal_check(self, inout):
		"""
		Removes lines where xn,yn are the same as xn-2, yn-2 (bouncing between craters)

		:param inout: Numpy array input.  Must have size [:, 22]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 22]
		"""
		inout = inout[np.where((inout[:, 1] != inout[:, 16]) & (inout[:, 2] != inout[:, 17]))]
		return inout

	def match_speed(self, inout):
		"""
		Checks that the velocity of each side of the jump are the same.

		:param inout: Numpy array input.  Must have size [:, 22]

		:returns: np.ndarray
			-out - Output numpy array with the shape [:, 22]
		"""
		inout = inout[np.isclose(inout[:, 8], inout[:, 19], rtol=self.sper, atol=self.spea)]
		return inout

	#def draw_box(self, img, points):
		#"""Draws a box.
		#"""
		#xbox, ybox, wbox, hbox = cv2.boundingRect(points)
		#cv2.rectangle(img, (xbox, ybox), (xbox+wbox, ybox+hbox), (0, 255, 0), 2)
		#return img

	def draw_rotated_box(self, img, points):
		"""
		Draws a rotated box which encloses the points in question.  The box is converted to its
		own set of points using the OpenCV method.  Then, these points are converted to intergers
		with Numpy.  The box is drawn onto the image with a mask and popped back out.  The boxes
		which are drawn will be 75% transparent.

		:param img: The image the points will be projected on.  It should be an OpenCV image object.
		:param points: Input points of interest to highlight with a box.  Should be a Numpy object
			with the shape [:, 7]

		:returns: OpenCVimage
			-added_image - The output image with the box drawn on it.
		"""
		rect = cv2.minAreaRect(points)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		mask = img
		cv2.drawContours(mask, [box], 0, self.fill, self.width)
		added_image = cv2.addWeighted(img, 0.75, mask, 0.25, 0)
		return added_image

	def set_pos_frame(self, pfs):
		"""functions to set the local version of set_pos_frame"""
		self.pfs = pfs
		return
