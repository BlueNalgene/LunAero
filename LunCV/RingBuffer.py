#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is a buffering class used for the LunAero prototype processor
'''

import gc
import math
import os

import numpy as np
# TODO remove me?
from scipy import stats

import cv2

class RingBufferClass():
	'''This is a buffering class used for the LunAero prototype processor
	'''

	# Reserved memory spaces for ring buffer lists
	aaa = []
	bbb = []
	# Reserved memory spaces for information about contour details
	ttt = []
	rrr = []
	xxx = []
	yyy = []
	# Reserved memory space for our working directory path.
	procpath = []
	# Tolerances factors.  Values are the rel. tolerance and abs. tolerance of variable.
	# Relative tolerance is the least significant digit.
	# Absolute tolerance is the threshold for giving up.  Numpy is weird on this.
	# The numpy version absolute(a - b) <= (atol + rtol * absolute(b)) is not reversible,
	# but that shouldn't matter for our stuff because of the implicit ordering here.
	# For contour radius
	radr = 10
	rada = 0.0
	# For contour apparent speed
	sper = 2
	spea = 2e-5 # Should not be zero, because a zero speed is possible
	# For angle of directional vector
	angr = 1e-3
	anga = 2e-5 # Should not be zero, because a zero angle is possible

	def __init__(self, pos_frame, last, procpath):
		# Set self.procpath to be the path determined in processor.py
		self.procpath = procpath
		# Numpy, quit using scientific notation, its painful
		np.set_printoptions(suppress=True)
		# TODO handler for when the directory already exists should be smarter
		try:
			os.mkdir(self.procpath)
		except FileExistsError:
			pass
		os.mkdir(self.procpath + '/orig_w_birds')
		os.mkdir(self.procpath + '/mixed_contours')
		# Create a new empty file for our csv output
		fff = self.procpath + '/longer_range_output.csv'
		with open(fff, 'w') as fff:
			fff.write('')
		# If we are not starting at frame zero, fudge some empty frames in there
		if pos_frame > 0:
			emptyslug = np.zeros((1080, 1920), dtype='uint8')
			for i in range(0, last):
				aaa = procpath + '/Frame_minus_{0}'.format(i)+'.npy'
				np.save(aaa, emptyslug)
		return

	def re_init(self, pos_frame, last):
		'''This function is called at the beginning of a main loop to
		clean up some of the leftovers from a previous frame
		If we don't call this, the ringbuffer may still have information stored from the previous
		run, and this can mess up our results.
		aka: magic function, do not touch.
		'''
		self.aaa = []
		self.bbb = []
		tempt = self.ttt
		tempr = self.rrr
		tempx = self.xxx
		tempy = self.yyy
		self.ttt = []
		self.rrr = []
		self.xxx = []
		self.yyy = []
		for i in enumerate(tempt):
			if tempt[i[0]] >= (pos_frame - last):
				self.ttt.append(tempt[i[0]])
				self.xxx.append(tempx[i[0]])
				self.yyy.append(tempy[i[0]])
				self.rrr.append(tempr[i[0]])

	def ringbuffer_cycle(self, pos_frame, img, last):
		'''Saves the contours from the image in a ring buffer.
		'''
		filename = self.procpath + '/Frame_minus_0.npy'
		np.save(filename, img)

		for i in range(last, 0, -1):
			if pos_frame == 0:
				continue
			elif (pos_frame - i + 1) >= 0:
				try:
					# Save as name(i) from...the file that used to be name(i-1)
					self.aaa = self.procpath + '/Frame_minus_{0}'.format(i-2)+'.npy'
					self.bbb = self.procpath + '/Frame_minus_{0}'.format(i-1)+'.npy'
					oldone = np.load(self.aaa)
					np.save(self.bbb, oldone)
				except FileNotFoundError:
					pass
		return

	def ringbuffer_process(self, pos_frame, img, last):
		'''Access the existing ringbuffer to get information about the last frames.
		Perform actions within.
		'''
		self.bbb = np.load(self.procpath + '/Frame_minus_0.npy')
		if pos_frame == 0:
			pass
		elif pos_frame >= last:
			for i in range(last, 1, -1):
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

			if self.ttt:
				img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		return img

	def get_centers(self, pos_frame, contours):
		'''Get the contours and centers of them should they exist.
		'''
		cnt = contours[0]
		for cnt in contours:
			perimeter = cv2.arcLength(cnt, True)
			if perimeter > 8 and perimeter < 200:
				(xpos, ypos), radius = cv2.minEnclosingCircle(cnt)
				self.ttt.append(pos_frame)
				self.rrr.append(radius)
				self.xxx.append(xpos)
				self.yyy.append(ypos)
		return

	def centers_local(self, pos_frame):
		'''Process local centers as a cyan line.
		'''

		goodlist = np.empty((0, 4), np.float32)

		# Comparitor counter for individual frames
		for i in range(0, len(self.xxx)):
			for j in range(0, len(self.xxx)):

				# Check that we are looking at contours on different frames
				if self.ttt[i] != self.ttt[j]:

					# Check that the size change of the contours is not drastic.
					if abs(self.rrr[i] - self.rrr[j]) < 5:

						# Get difference between points
						pythag = math.sqrt((self.xxx[i] - self.xxx[j])**2 + (self.yyy[i] - self.yyy[j])**2)
						# Get the ratio between previous number and Frame
						if pos_frame - self.ttt[i]:
							pass
						else:
							pythag = pythag/((pos_frame - self.ttt[i]) + 1)
							#print(((pos_frame - self.ttt[i]) + 1), pythag)

							# If the score is good, the relationship passes the test.
							if pythag >= 5 and pythag <= 300:

								# Add these points to our good list.
								goodlist = np.append(goodlist, np.array([[\
									self.ttt[i], self.xxx[i], self.yyy[i], self.rrr[i]]]), axis=0)
								goodlist = np.append(goodlist, np.array([[\
									self.ttt[j], self.xxx[j], self.yyy[j], self.rrr[j]]]), axis=0)

		if goodlist.size != 0:
			goodlist = np.unique(goodlist, axis=0)
		return goodlist

	def bird_range(self, pos_frame, img, frame, gdl, last):
		'''An adaptable range processor, takes values of each frame, then runs those values vs.
		previous frame values
		'''

		# Local constants
		radii_minimum = 2
		#radii_maximum = 5000
		#speed_minimum = 2
		#speed_maximum = 100

		# No scientific notation please.
		np.set_printoptions(suppress=True)

		# Process Numpy Array with floats in a format:
		gdl = np.reshape(gdl, (-1, 4))
		gdl = np.unique(gdl, axis=0)

		# Multiply rows to increase accuracy
		# Make an int only array (multiplied by 10 to include significant digit decimal) for x,y
		# locaions.  Remember the 10x!
		gdl = (gdl * np.array([1, 10, 10, 10000], np.newaxis)).astype(dtype=int)

		# Remove rows with radii less than a certain size
		gdl = gdl[np.greater_equal(gdl[:, 3], radii_minimum), :]

		gdlmix = np.column_stack((gdl[:, 1].astype(dtype=int),\
			gdl[:, 2].astype(dtype=int)))
		fourlist = np.empty((0, 4), int)
		for i in range(0, np.size(gdlmix[:, 0])):
			for j in range(0, np.size(gdlmix[:, 0])):
				fourlist = np.vstack((fourlist, np.hstack((gdlmix[i], gdlmix[j]))))

		# Group by frame
		gdlmin0 = gdl[np.equal(gdl[:, 0], pos_frame), :]
		gdlmin1 = gdl[np.equal(gdl[:, 0], pos_frame-1), :]
		gdlmin2 = gdl[np.equal(gdl[:, 0], pos_frame-2), :]
		gdlmin3 = gdl[np.equal(gdl[:, 0], pos_frame-3), :]

		# Generate empty array to hold our final results from the analysis
		points = np.empty((0, 2), int)

		# Generate empty storage array
		fourlist = np.empty((0, 9), int)

		# Process each sequential image for distance
		fourlistx = self.stackdistance(gdlmin0, gdlmin1)
		fourlisty = self.stackdistance(gdlmin1, gdlmin2)
		fourlistz = self.stackdistance(gdlmin2, gdlmin3)

		# Cleanup to prevent overeating memory
		del gdl, gdlmin0, gdlmin1, gdlmin2, gdlmin3

		# Get Speed for each item on the list
		fourlistx = self.getspeed(fourlistx)
		fourlisty = self.getspeed(fourlisty)
		fourlistz = self.getspeed(fourlistz)

		# Get direction for each item on the list
		fourlistx = self.getdir(fourlistx)
		fourlisty = self.getdir(fourlisty)
		fourlistz = self.getdir(fourlistz)

		# Run a size test.  The radius should be relatively constant.
		fourlistx = fourlistx[np.isclose(fourlistx[:, 3], fourlistx[:, 7], rtol=self.radr, atol=self.rada)]
		fourlisty = fourlisty[np.isclose(fourlisty[:, 3], fourlisty[:, 7], rtol=self.radr, atol=self.rada)]
		fourlistz = fourlistz[np.isclose(fourlistz[:, 3], fourlistz[:, 7], rtol=self.radr, atol=self.rada)]

		# Compare the generated lists (second order)
		fourlistn = self.combineperms(fourlistx, fourlisty)
		fourlisty = self.combineperms(fourlisty, fourlistz)
		fourlistz = self.combineperms(fourlistx, fourlistz)
		fourlistx = fourlistn
		del fourlistn

		# Test distance/direction
		fourlistx = self.distdirtest(fourlistx)
		fourlisty = self.distdirtest(fourlisty)
		fourlistz = self.distdirtest(fourlistz)

		#If we have empty lists, we need to make them empty with the right size
		fourlistx = self.gapinghole(fourlistx)
		fourlisty = self.gapinghole(fourlisty)
		fourlistz = self.gapinghole(fourlistz)

		# NOTE this only returns a bulk of all birds.  It does not loop over groupings. Yet.
		# TODO make tunable isclose value variables

		## If enabled, color each contour layer.
		#frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
		#frame = self.color_contours(frame)

		##One list to rule them all
		if np.size(fourlistx, 0) == 0 and np.size(fourlisty, 0) == 0 and np.size(fourlistz, 0) == 0:
			gc.collect()
			return img
		# TODO be smarter about this vstacking, work it for individual linear ranges.
		print("x: ", fourlistx.shape, "\ny: ", fourlisty.shape, "\nz: ", fourlistz.shape, "\n")
		fourlist = np.vstack((fourlistx, fourlisty, fourlistz))
		del fourlistx, fourlisty, fourlistz

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
			False, False, False,\
			False, True, True, False, \
			False, True, True, False, \
			False, False, False]])
		points = np.reshape(fourlist[np.all(mask*[fourlist], axis=0)], (-1, 4, 2))
		points = np.unique(points, axis=0)
		points = np.divide(points, 10)
		points = points.astype('int')
		# Each grouping of points should be boxed
		for ppp in points[:]:
			img = self.draw_rotated_box(img, ppp)

		## Everything past this point is "good"
		#points = np.vstack((points, fourlist[:, 1:3], fourlist[:, 5:7], \
			#fourlist[:, 12:14], fourlist[:, 16:18]))
		#points = np.unique(points, axis=0)
		## Put points into a simplified x y format so they can be read.
		#points = np.divide(points, 10)
		#points = points.astype('int')

		#TEST
		print("fourlist\n", fourlist)
		print("points\n", points)

		## draw a box that encloses all of the points
		#img = self.draw_rotated_box(img, points)

		# Save contour information to file
		with open(self.procpath + '/longer_range_output.csv', 'a') as fff:
			outputline = str('%09d' % pos_frame) + '\n'
			fff.write(outputline)
		with open(self.procpath + '/longer_range_output.csv', 'ab') as fff:
			np.savetxt(fff, fourlist, delimiter=",")

		# Save original image which is believed to contain birds
		cv2.imwrite(self.procpath + '/orig_w_birds/original_%09d.png' % pos_frame, frame)

		# Overlay the boxed birds to the original image
		frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
		added_image = cv2.addWeighted(frame, 0.5, img, 0.5, 0)

		# Save  mixed image to file
		cv2.imwrite(self.procpath + '/mixed_contours/contours_%09d.png' % pos_frame, added_image)

		#Cleanup what we have left to free memory
		del fourlist
		gc.collect()

		return img

	def stackdistance(self, in1, in2):
		'''Blah TODO
		templist = x row, 8->9 columns
		'''
		# Bird speed constants
		smin = 2
		smax = 200

		# Start empty Numpy array
		out = np.empty((0, 8), int)

		# Some local variables
		sizei = np.size(in1, 0)
		sizej = np.size(in2, 0)

		# Kill early check
		if sizei & sizej:
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
		'''Blah TODO
		'''
		if np.size(inout, 0) == 0:
			return inout
		inout = np.column_stack((inout, np.divide(inout[:, 8], np.abs(np.subtract(inout[:, 0], \
			inout[:, 4])))))
		return inout

	def getdir(self, inout):
		'''Blah TODO
		'''
		if np.size(inout, 0) == 0:
			return inout
		inout = np.column_stack((inout, np.arctan2(np.abs(np.subtract(inout[:, 2], inout[:, 6])), \
			np.abs(np.subtract(inout[:, 1], inout[:, 5])))*(180/np.pi)))
		return inout

	def combineperms(self, in1, in2):
		'''Combines numpy arrays in a row-by-row type of permutation.  Put two arrays in,
		and pop out just one!
		'''
		# Combine columns using the repeat and tile method
		out = np.column_stack((np.repeat(in1, np.size(in2, 0), axis=0), \
			np.tile(in2, (np.size(in1, 0), 1))))
		return out

	def distdirtest(self, inout):
		'''Tests for distance and direction without bounds for compared list items.
		Keeps good ones.
		'''
		if np.size(inout, 0) < 20:
			return inout
		# Test distance
		inout = inout[np.isclose(inout[:, 8], inout[:, 19], rtol=self.sper, atol=self.spea)]
		# Test direction
		inout = inout[np.isclose(inout[:, 10], inout[:, 21], rtol=self.angr, atol=self.anga)]
		return inout

	def gapinghole(self, inout):
		'''If it is empty, make it empty with the right size
		'''
		if np.size(inout, 0) == 0:
			inout = np.empty((0, 22), int)
		return inout


	def draw_box(self, img, points):
		'''Draws a box.
		'''
		xbox, ybox, wbox, hbox = cv2.boundingRect(points)
		cv2.rectangle(img, (xbox, ybox), (xbox+wbox, ybox+hbox), (0, 255, 0), 2)
		return img

	def draw_rotated_box(self, img, points):
		'''Draws a rotated boxPoints
		'''
		rect = cv2.minAreaRect(points)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		mask = img
		cv2.drawContours(mask, [box], 0, (255, 0, 63), 1)
		added_image = cv2.addWeighted(img, 0.75, mask, 0.25, 0)
		return added_image

	#def color_contours(self, img):
		#'''Blah TODO
		#'''
		#for i in range(0, 5):
			#contours = self.procpath + '/Frame_minus_{0}'.format(5-i)+'.npy'
			#try:
				#cv2.drawContours(img, contours, -1, (0,(255-(51*i)),255), 1)
			#except TypeError:
				#pass
		#return img
