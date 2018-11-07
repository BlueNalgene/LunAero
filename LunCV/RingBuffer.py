#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This is a buffering class used for the LunAero prototype processor
'''

import numpy as np

import cv2

class RingBufferClass():
	'''This is a buffering class used for the LunAero prototype processor
	'''

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
					aaa = '/scratch/whoneyc/Frame_minus_{0}'.format(i-2)+'.npy'
					bbb = '/scratch/whoneyc/Frame_minus_{0}'.format(i-1)+'.npy'
					oldone = np.load(aaa)
					np.save(bbb, oldone)
				except FileNotFoundError:
					pass
		return

	def ringbuffer_process(self, pos_frame, img, last):
		'''Access the existing ringbuffer to get information about the last frames.
		Perform actions within.
		'''
		bbb = np.load('/scratch/whoneyc/Frame_minus_0.npy')
		if pos_frame == 0:
			pass
		elif pos_frame >= last:
			for i in range(last, 1, -1):
				try:
					aaa = '/scratch/whoneyc/Frame_minus_{0}'.format(i-1)+'.npy'
					aaa = np.load(aaa)
					bbb = np.add(aaa, bbb)
					np.save('/scratch/whoneyc/Frame_minus_0.npy', bbb)
				except TypeError:
					print("bailing on error")
			bbb = np.load('/scratch/whoneyc/Frame_minus_0.npy')
			bbb[bbb > 1] = 0
			bbb[bbb == 1] = 255
			np.save('/scratch/whoneyc/Frame_mixed.npy', bbb)

			img = np.load('/scratch/whoneyc/Frame_mixed.npy')
			_, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
			_, contours, _ = cv2.findContours(thresh, 2, 1)

			centers = []
			if contours:
				centers = mixed_centers(contours)

			img[img > 0] = 255

			if centers:
				img = centers_proc(pos_frame, centers, img)
		return img
