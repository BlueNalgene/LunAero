#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is a buffering class used for the LunAero prototype processor
'''

import math
import numpy as np

from scipy import stats

import cv2

class RingBufferClass():
	'''This is a buffering class used for the LunAero prototype processor
	'''

	aaa = []
	bbb = []
	ttt = []
	rrr = []
	xxx = []
	yyy = []

	def __init__(self):
		np.set_printoptions(suppress=True)
		return

	def re_init(self, pos_frame, last):
		'''This function is called at the beginning of a main loop to
		clean up some of the leftovers from a previous frame
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
		for i in range(0, len(tempt)):
			if tempt[i] >= (pos_frame - last):
				self.ttt.append(tempt[i])
				self.xxx.append(tempx[i])
				self.yyy.append(tempy[i])
				self.rrr.append(tempr[i])

	def ringbuffer_cycle(self, pos_frame, img, last):
		'''Saves the contours from the image in a ring buffer.
		'''
		np.save('/scratch/whoneyc/Frame_minus_0.npy', img)

		for i in range(last, 0, -1):
			if pos_frame == 0:
				continue
			elif (pos_frame - i + 1) >= 0:
				try:
					# Save as name(i) from...the file that used to be name(i-1)
					self.aaa = '/scratch/whoneyc/Frame_minus_{0}'.format(i-2)+'.npy'
					self.bbb = '/scratch/whoneyc/Frame_minus_{0}'.format(i-1)+'.npy'
					oldone = np.load(self.aaa)
					np.save(self.bbb, oldone)
				except FileNotFoundError:
					pass
		return

	def ringbuffer_process(self, pos_frame, img, last):
		'''Access the existing ringbuffer to get information about the last frames.
		Perform actions within.
		'''
		self.bbb = np.load('/scratch/whoneyc/Frame_minus_0.npy')
		if pos_frame == 0:
			pass
		elif pos_frame >= last:
			for i in range(last, 1, -1):
				try:
					self.aaa = '/scratch/whoneyc/Frame_minus_{0}'.format(i-1)+'.npy'
					self.aaa = np.load(self.aaa)
					self.bbb = np.add(self.aaa, self.bbb)
					np.save('/scratch/whoneyc/Frame_minus_0.npy', self.bbb)
				except TypeError:
					print("bailing on error")
			self.bbb = np.load('/scratch/whoneyc/Frame_minus_0.npy')
			self.bbb[self.bbb > 1] = 0
			self.bbb[self.bbb == 1] = 255
			np.save('/scratch/whoneyc/Frame_mixed.npy', self.bbb)

			img = np.load('/scratch/whoneyc/Frame_mixed.npy')
			#_, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
			#_, contours, _ = cv2.findContours(thresh, 2, 1)

			#if contours:
				#self.get_centers(pos_frame, contours)

			img[img > 0] = 255

			if self.ttt:
				img = self.centers_proc(pos_frame, img)
		return img

	def get_centers(self, pos_frame, contours):
		'''Get the contours and centers of them should they exist.
		'''
		cnt = contours[0]
		for cnt in contours:
			perimeter = cv2.arcLength(cnt, True)
			if perimeter > 8 and perimeter < 200:
				(xpos, ypos), radius = cv2.minEnclosingCircle(cnt)
				#(xxx, yyy), radius = cv2.minEnclosingCircle(cnt)
				self.ttt.append(pos_frame)
				self.rrr.append(radius)
				self.xxx.append(xpos)
				self.yyy.append(ypos)
				#centroid = (int(pos_frame), (xxx), int(yyy))
				#self.centers.append(np.round(centroid))
		return

	def centers_proc(self, pos_frame, img):
		'''Process centers that exist for lines
		'''

		slope, intercept, _, _, _ = stats.linregress(self.xxx, self.yyy)
		if math.isnan(slope) or math.isnan(intercept):
			pass
		else:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
			cv2.line(img, (0, int(slope*0+intercept)), (10000000, int(slope*10000000+intercept)), \
				(0, 0, 255), 2)
			with open('/scratch/whoneyc/outputslopes.csv', 'a') as fff:
				thestring = str(pos_frame) + ',' + str(slope) + ',' + str(intercept) +'\n'
				fff.write(thestring)
		return img

	def centers_local(self, pos_frame, img):
		'''Process local centers as a cyan line.
		'''

		goodlist = np.empty((0, 8), np.float32)

		# Comparitor counter for individual frames
		for i in range(0, len(self.xxx)):
			for j in range(0, len(self.xxx)):

				# Check that we are looking at contours on different frames
				if self.ttt[i] != self.ttt[j]:

					# Check that the size change of the contours is not drastic.
					if abs(self.rrr[i] - self.rrr[j]) < 1:

						# Get difference between points
						pythag = math.sqrt((self.xxx[i] - self.xxx[j])**2 + (self.yyy[i] - self.yyy[j])**2)
						# Get the ratio between previous number and Frame
						if pos_frame - self.ttt[i]:
							pass
						else:
							pythag = pythag/((pos_frame - self.ttt[i]) + 1)
							#print(((pos_frame - self.ttt[i]) + 1), pythag)

							# If the score is good, the relationship passes the test.
							if pythag >= 5 and pythag <= 50:
								# Draw it visually
								cv2.line(img, (int(self.xxx[i]), int(self.yyy[i])), (int(self.xxx[j]),\
									int(self.yyy[j])), (255, 255, 0), 2)

								# Add these points to our good list.
								goodlist = np.append(goodlist, np.array([[\
									self.ttt[i], self.xxx[i], self.yyy[i], self.rrr[i], \
										self.ttt[j], self.xxx[j], self.yyy[j], self.rrr[j]]]), axis=0)

		if goodlist.size != 0:
			goodlist = np.unique(goodlist, axis=0)
		return goodlist

	def longer_range(self, pos_frame, last, img, goodlist):
		'''Look for longer range linearity in the goodlist
		Draws a green box around those points.
		'''

		# Process Numpy Array with floats in a format:
		#    [[ pos[i] x[i] y[i] radius[i] pos[j] x[j] y[j] radius[j]
		#     [ pos[i] x[i] y[i] radius[i] pos[j] x[j] y[j] radius[j]]
		goodlist = np.reshape(goodlist, (-1, 4))
		# Now looks like:
		#    [[ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]
		#     [ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]]
		goodlist = np.unique(goodlist, axis=0)
		# Now looks like:
		#    [[ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]]
		for i in range(0, np.size(goodlist, 0)):
			potentialround1 = np.array(goodlist[i,:])
			for j in range(0, np.size(goodlist, 0)):
				# Test for frame difference.
				if goodlist[j,:][0] < goodlist[i,:][0]:
					potentialround2 = np.vstack((potentialround1, goodlist[j,:]))
					for k in range(0, np.size(goodlist, 0)):
						if goodlist[k,:][0] < goodlist[j,:][0]:
							# Now we have interesting rows i, j, and k
							potentialround3 = np.vstack((potentialround2, goodlist[k,:]))
							for l in range(0, np.size(goodlist, 0)):
								if goodlist[l,:][0] < goodlist[k,:][0]:
									# Now we have interesting rows i, j, and k
									potentialround4 = np.vstack((potentialround3, goodlist[k,:]))
									# We rotate the array 90 degrees so that all of the entries are lined up by type.
									potrot = np.rot90(potentialround4)
									# We find the difference between each entry in the matrix in each row.
									# Should give a 1D matrix of size 11
									# The 3rd, 6th, 9th, and 11th element of that array will be useless
									# We add another uselss element to the end (the 15th element)
									result = np.ediff1d(potrot, to_end=0)
									# We reshape this result so we have two rows of diff and a useless col
									result = np.reshape(result, (4, 4))
									# And we remove the useless col
									result = np.delete(result, 3, 1)
									# What we have now should be a two column matrix.
									# Each row is a pair of differences in the order: r, y, x, t
									# We now repeat on this matrix.
									#print(result)
									result = np.ediff1d(result, to_end=0)
									result = np.reshape(result, (4, 3))
									result = np.delete(result, 2, 1)
									#print(result)
									result = np.ediff1d(result, to_end=0)
									result = np.reshape(result, (4, 2))
									result = np.delete(result, 1, 1)
									# Speed calculation
									speedx = (result[2]+1)/(abs(result[3])+1)
									speedy = (result[1]+1)/(abs(result[3])+1)
									# Speed test
									if abs(speedx) < 10 and abs(speedy) < 10:
										print(speedx, speedy)
										# put a box that encloses all of the points
										points = np.delete(potentialround4, 3, 1)
										points = np.delete(points, 0, 1)
										points = points.astype('int')
										xbox, ybox, wbox, hbox = cv2.boundingRect(points)
										cv2.rectangle(img, (xbox, ybox), (xbox+wbox, ybox+hbox), (0, 255, 0), 2)
										# Save to file
										with open('/scratch/whoneyc/longer_range_output.csv', 'a') as fff:
											outputline = str(pos_frame) + '\n'
											fff.write(outputline)
										with open('/scratch/whoneyc/longer_range_output.csv', 'ab') as fff:
											np.savetxt(fff, potentialround4, delimiter=",")
