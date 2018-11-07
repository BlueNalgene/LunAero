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
	centers = []
	xxx = []
	yyy = []

	def re_init(self):
		self.aaa = []
		self.bbb = []
		self.centers = []
		self.xxx = []
		self.yyy = []

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
			_, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
			_, contours, _ = cv2.findContours(thresh, 2, 1)

			if contours:
				self.centers = self.mixed_centers(contours)

			img[img > 0] = 255

			if self.centers:
				img = self.centers_proc(pos_frame, img)
		return img

	def mixed_centers(self, contours):
		'''Get the contours and centers of them should they exist.
		'''
		cnt = contours[0]
		for cnt in contours:
			perimeter = cv2.arcLength(cnt, True)
			if perimeter > 8 and perimeter < 200:
				(xxx, yyy), _ = cv2.minEnclosingCircle(cnt)
				#(xxx, yyy), radius = cv2.minEnclosingCircle(cnt)
				centroid = (int(xxx), int(yyy))
				self.centers.append(np.round(centroid))
		return self.centers

	def centers_proc(self, pos_frame, img):
		'''Process centers that exist for lines
		'''

		for i in self.centers:
			self.xxx.append(i[0])
			self.yyy.append(i[1])
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
