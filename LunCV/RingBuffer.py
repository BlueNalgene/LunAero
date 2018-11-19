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
		with open('/scratch/whoneyc/longer_range_output.csv', 'w') as fff:
			fff.write('')
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
		for i in enumerate(tempt):
			if tempt[i[0]] >= (pos_frame - last):
				self.ttt.append(tempt[i[0]])
				self.xxx.append(tempx[i[0]])
				self.yyy.append(tempy[i[0]])
				self.rrr.append(tempr[i[0]])

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
							if pythag >= 5 and pythag <= 200:

								# Add these points to our good list.
								goodlist = np.append(goodlist, np.array([[\
									self.ttt[i], self.xxx[i], self.yyy[i], self.rrr[i]]]), axis=0)
								goodlist = np.append(goodlist, np.array([[\
									self.ttt[j], self.xxx[j], self.yyy[j], self.rrr[j]]]), axis=0)

		if goodlist.size != 0:
			goodlist = np.unique(goodlist, axis=0)
		return goodlist

	def simple_regression(self, pos_frame, img):
		'''Places a line through the frame which attempts to fit all of the points on the plot.
		This is done by least squares regression.
		It is not very useful, but I have kept it just in case.
		'''

		slope, intercept, _, _, _ = stats.linregress(self.xxx, self.yyy)
		if math.isnan(slope) or math.isnan(intercept):
			pass
		else:
			#img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
			# Draw an estimate line
			cv2.line(img, (0, int(slope*0+intercept)), (10000000, int(slope*10000000+intercept)), \
				(0, 0, 255), 2)
			with open('/scratch/whoneyc/outputslopes.csv', 'a') as fff:
				thestring = str(pos_frame) + ',' + str(slope) + ',' + str(intercept) +'\n'
				fff.write(thestring)
		return img

	def local_linear(self, pos_frame, img, goodlist):
		'''Compares two points.  If the points are linked with pythag, then draws a line between them.
		Works ok for visual spotting.
		'''
		if goodlist.size != 0:
			with open('/scratch/whoneyc/local_linear_output.csv', 'a') as fff:
				outputline = str('%09d' % pos_frame) + '\n'
				fff.write(outputline)
		for i in range(0, len(self.xxx)):
			for j in range(0, len(self.xxx)):
				# Draw a line through the points
				cv2.line(img, (int(self.xxx[i]), int(self.yyy[i])), (int(self.xxx[j]),\
					int(self.yyy[j])), (255, 255, 0), 2)
				with open('/scratch/whoneyc/longer_range_output.csv', 'a') as fff:
					outputline = str(int(self.xxx[i])) + ',' + str(int(self.yyy[i])) + ',' + \
						str(int(self.xxx[j])) + ',' + str(int(self.yyy[j])) + '\n'
					fff.write(outputline)
		return img

	def middle_range(self, pos_frame, img, frame, gdl):
		'''Look for longer range linearity in the goodlist
		Draws a green box around those points.
		'''

		# No scientific notation please.
		np.set_printoptions(suppress=True)

		print(gdl)
		long_range_switch = False
		# Process Numpy Array with floats in a format:
		#    [[ pos[i] x[i] y[i] radius[i] pos[j] x[j] y[j] radius[j]
		#     [ pos[i] x[i] y[i] radius[i] pos[j] x[j] y[j] radius[j]]
		gdl = np.reshape(gdl, (-1, 4))
		# Now looks like:
		#    [[ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]
		#     [ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]]
		gdl = np.unique(gdl, axis=0)
		# Now looks like:
		#    [[ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]]

		# Make a size range thing
		counter = range(0, np.size(gdl, 0))
		# For everything in the list iterated twice
		for i in counter:
			pr1 = np.array(gdl[i])
			for j in counter:
				# Test for frame difference.
				if gdl[j][0] > gdl[i][0] and gdl[j][3] > 2 and gdl[i][3] > 2:
					pr2 = np.vstack((pr1, gdl[j]))
					for k in counter:
						if gdl[k][0] > gdl[j][0] and gdl[k][3] > 2:
							# Now we have interesting rows i, j, and k
							pr3 = np.vstack((pr2, gdl[k]))

							# We rotate the array 90 degrees so that all of the entries are lined up by type.
							potrot = np.rot90(pr3)

							# Check that it is possible that these points are sequential in time.
							sequence = np.empty((1, 0), np.float32)
							for x in potrot[3]:
								sequence = np.append(sequence, x)
							if np.size(sequence) != np.size(np.unique(sequence)):
								continue

							# Check that the linearity is good.
							sequence = np.empty((1, 0), np.float32)
							for x in range(1, 3):
								direct = math.atan((potrot[1][x] - potrot[1][0])/\
									(potrot[2][x] - potrot[2][0]))
								sequence = np.append(sequence, direct)
							# Check if they deviate by ~1 degrees
							if abs(np.ediff1d(sequence)) > 0.02:
								continue

							# Check that the lengths are similar
							sequence = np.empty((1, 0), np.float32)
							for x in range(0, 2):
								pythag = math.sqrt((potrot[2][x+1] - potrot[2][x])**2 +\
									(potrot[1][x+1] - potrot[1][x])**2)
								pythag = pythag/(potrot[3][x+1] - potrot[3][x])
								sequence = np.append(sequence, pythag)
							if abs(np.ediff1d(sequence)) > 10:
								continue
							

							# We find the difference between each entry in the matrix in each row.
							# Should give a 1D matrix of size 11
							# The 3rd, 6th, 9th, and 11th element of that array will be useless
							# We add another uselss element to the end (the 15th element)
							result = np.ediff1d(potrot, to_end=0)
							# We reshape this result so we have two rows of diff and a useless col
							result = np.reshape(result, (4, 3))
							# And we remove the useless col
							result = np.delete(result, 2, 1)

							# What we have now should be a two column matrix.
							# Each row is a pair of differences in the order: r, y, x, t
							# We now repeat on this matrix.
							result = np.ediff1d(result, to_end=0)
							result = np.reshape(result, (4, 2))
							result = np.delete(result, 1, 1)

							# Run a size test.  The radius should be relatively constant.
							if abs(result[0]) > 4:
								continue

							long_range_switch = True
							# Put points into a simplified x y format so they can be read.
							points = np.delete(pr3, 3, 1)
							points = np.delete(points, 0, 1)
							points = points.astype('int')
							# draw a box that encloses all of the points
							img = self.draw_rotated_box(img, points)
							# Save to file
							with open('/scratch/whoneyc/longer_range_output.csv', 'a') as fff:
								outputline = str('%09d' % pos_frame) + '\n'
								fff.write(outputline)
							with open('/scratch/whoneyc/longer_range_output.csv', 'ab') as fff:
								np.savetxt(fff, pr3, delimiter=",")
		# Output screenshots
		if long_range_switch:
			cv2.imwrite('/scratch/whoneyc/original_%09d.png' % pos_frame, frame)
			frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
			added_image = cv2.addWeighted(frame, 0.5, img, 0.5, 0)
			cv2.imwrite('/scratch/whoneyc/contours_%09d.png' % pos_frame, added_image)
		return

	def longer_range(self, pos_frame, img, frame, gdl):
		'''Look for longer range linearity in the goodlist
		Draws a green box around those points.
		'''

		# No scientific notation please.
		np.set_printoptions(suppress=True)

		print(gdl)
		long_range_switch = False
		# Process Numpy Array with floats in a format:
		#    [[ pos[i] x[i] y[i] radius[i] pos[j] x[j] y[j] radius[j]
		#     [ pos[i] x[i] y[i] radius[i] pos[j] x[j] y[j] radius[j]]
		gdl = np.reshape(gdl, (-1, 4))
		# Now looks like:
		#    [[ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]
		#     [ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]]
		gdl = np.unique(gdl, axis=0)
		# Now looks like:
		#    [[ pos[i] x[i] y[i] radius[i]
		#     [ pos[j] x[j] y[j] radius[j]]

		# Make a size range thing
		counter = range(0, np.size(gdl, 0))
		# For everything in the list iterated twice
		for i in counter:
			pr1 = np.array(gdl[i])
			for j in counter:
				# Test for frame difference.
				if gdl[j][0] > gdl[i][0] and gdl[j][3] > 2 and gdl[i][3] > 2:
					pr2 = np.vstack((pr1, gdl[j]))
					for k in counter:
						if gdl[k][0] > gdl[j][0] and gdl[k][3] > 2:
							# Now we have interesting rows i, j, and k
							pr3 = np.vstack((pr2, gdl[k]))
							for l in counter:
								if gdl[l][0] > gdl[k][0] and gdl[l][3] > 2:
									# Now we have interesting rows i, j, and k
									pr4 = np.vstack((pr3, gdl[k]))
									# We rotate the array 90 degrees so that all of the entries are lined up by type.
									potrot = np.rot90(pr4)
									print(potrot)
									#####################TODO here

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
									result = np.ediff1d(result, to_end=0)
									result = np.reshape(result, (4, 3))
									result = np.delete(result, 2, 1)

									result = np.ediff1d(result, to_end=0)
									result = np.reshape(result, (4, 2))
									result = np.delete(result, 1, 1)
									# Speed calculation
									speedx = (result[2]+1)/(abs(result[3])+1)
									speedy = (result[1]+1)/(abs(result[3])+1)

									#####################TODO
									#np.array(speedx, speedy)
									#np.hstack((result, speedx, speedy))
									#if result[0]/(np.mean(potrot, axis=0))[0] > 5:
										#continue

									# Speed test
									#if abs(speedx) < 150 and abs(speedy) < 150:
									long_range_switch = True
									# Put points into a simplified x y format so they can be read.
									points = np.delete(pr4, 3, 1)
									points = np.delete(points, 0, 1)
									points = points.astype('int')
									# draw a box that encloses all of the points
									img = self.draw_box(img, points)
									# Save to file
									with open('/scratch/whoneyc/longer_range_output.csv', 'a') as fff:
										outputline = str('%09d' % pos_frame) + '\n'
										fff.write(outputline)
									with open('/scratch/whoneyc/longer_range_output.csv', 'ab') as fff:
										np.savetxt(fff, pr4, delimiter=",")
		# Output screenshots
		if long_range_switch:
			cv2.imwrite('/scratch/whoneyc/original_%09d.png' % pos_frame, frame)
			frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
			added_image = cv2.addWeighted(frame, 0.5, img, 0.5, 0)
			cv2.imwrite('/scratch/whoneyc/contours_%09d.png' % pos_frame, added_image)
		return

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
		cv2.drawContours(mask, [box], 0, (255, 0, 63), -1)
		added_image = cv2.addWeighted(img, 0.75, mask, 0.25, 0)
		return added_image
