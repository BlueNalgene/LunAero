#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Commands for the Raspberry Pi Camera
To be activated from the moontracker.py base file
'''
import io
import threading
import time
import numpy as np
from PIL import Image

import picamera
import MotorControl

class CameraCommands():
	'''Commands for the Raspberry Pi Camera
	To be activated from the moontracker.py base file
	'''

	# Definitions used locally in this class
	CAMERA = picamera.PiCamera()
	MOC = MotorControl.MotorControl()
	STREAM = io.BytesIO()
	IMGTHRESH = 125

	import Lconfig
	HORDIM = Lconfig.HORDIM
	VERTDIM = Lconfig.VERTDIM
	HORTHRESHSTOP = Lconfig.HORTHRESHSTOP
	VERTTHRESHSTOP = Lconfig.VERTTHRESHSTOP
	LOSTRATIO = Lconfig.LOSTRATIO
	IMGTHRESH = Lconfig.IMGTHRESH
	CENX = Lconfig.CENY
	CENY = Lconfig.CENX

	iso = 400

	#thread = threading.Thread(target=self.forever_cap, args=())
	#event = threading.Event()
	#conn_lock = threading.Lock()
	#pool_lock = threading.Lock()
	#pool = []

	def __init__(self, interval=0.1):
		'''This init starts the screen captures in background
		Set the interval parameter to change the number of seconds between each capture
		'''
		self.interval = interval
		self.terminated = False
		self.startup_camera()
		#thread.start()
		return

	def startup_camera(self):
		'''Starts the camera with correct settings
		'''
		self.CAMERA.led = False
		self.CAMERA.video_stabilization = True
		self.CAMERA.resolution = (1920, 1080)
		self.CAMERA.color_effects = (128, 128) # turn camera to black and white

	def get_exp(self):
		'''returns the exposure speed of the camera
		'''
		exp = self.CAMERA.exposure_speed
		return exp

	def go_prev(self, prev):
		'''Preview size options
		'''

		if prev == 1:
			self.CAMERA.start_preview(fullscreen=False, window=(1200, -20, 640, 480))
		if prev == 2:
			self.CAMERA.start_preview(fullscreen=False, window=(800, -20, 1280, 960))
		if prev == 3:
			self.CAMERA.start_preview(fullscreen=False, window=(20, 400, 640, 480))
		if prev == 4:
			self.CAMERA.start_preview(fullscreen=False, window=(20, 200, 1280, 960))
		if prev == 5:
			self.CAMERA.start_preview(fullscreen=True)
		return prev

	def get_img(self):
		'''Capture an image and see how close it is to center
		'''
		#from Lconfig import IMGTHRESH, HORDIM, VERTDIM, self.CENX, CENY

		# Capture image and convert to monochrome np array
		#self.CAMERA.capture(self.STREAM, use_video_port=True, resize=\
			#(self.HORDIM, self.VERTDIM), format='jpeg')
		#img = Image.open(self.STREAM)
		img = Image.open('/var/tmp/LunAero/tmp.jpg')
		img = img.convert('L')
		img = img.point(lambda x: 0 if x < self.IMGTHRESH else 255, '1')
		img = np.asarray(img)

		# Get vector of row and columns, then scrub stray pixels
		cmx = np.sum(img, axis=0)
		cmy = np.sum(img, axis=1)
		cmx[cmx < 10] = 0
		cmy[cmy < 10] = 0

		# Get moment of the moon
		cmx = np.mean(np.nonzero(cmx))
		cmy = np.mean(np.nonzero(cmy))

		#ratio of white to black - used to tell if the moon is lost
		ratio = img.sum()/(self.HORDIM*self.VERTDIM)

		# Determines the difference of the center of mass from the center of the frame.
		# For x: if positive, shift right; if negative, shift left
		# For y: if positive, shift down; if negative, shift up
		diffx = self.CENX - cmx
		diffy = self.CENY - cmy
		return diffx, diffy, ratio, cmx, cmy

	def checkandmove(self):
		'''This checks the difference in thresholds
		'''
		#from Lconfig import LOSTRATIO, HORTHRESHSTOP, VERTTHRESHSTOP

		diffx, diffy, ratio, _, _ = self.get_img()
		if ratio < self.LOSTRATIO:
			# Default to 'moon is lost'
			rtn = 2
		else:
			if abs(diffx) > self.HORTHRESHSTOP:
				if diffx > 0:
					self.MOC.mot_left()
				else:
					self.MOC.mot_right()
				self.MOC.speed_up("X")
			if abs(diffy) > self.VERTTHRESHSTOP:
				if diffy > 0:
					self.MOC.mot_up()
				else:
					self.MOC.mot_down()
				self.MOC.speed_up("Y")
			if (abs(diffx) < self.HORTHRESHSTOP and self.MOC.dcB > 0):
				self.MOC.mot_stop("X")
			if (abs(diffy) < self.VERTTHRESHSTOP and self.MOC.dcA > 0):
				self.MOC.mot_stop("Y")
			if (abs(diffx) < self.HORTHRESHSTOP and abs(diffy) < self.VERTTHRESHSTOP):
				self.MOC.mot_stop("B")
				rtn = 1
			else:
				rtn = 0
		return rtn

	def shutdown_camera(self):
		'''Shuts down the camera and motor
		'''
		self.MOC.mot_stop("B")
		self.CAMERA.close()
		return

	def start_recording(self, outfile):
		'''Function must be in this program to segregate imports
		'''
		self.CAMERA.start_recording(outfile)
		return

	def stop_preview(self):
		'''Function must be in this program to segregate imports
		'''
		self.CAMERA.stop_preview()
		return

	def thresh_dec(self):
		'''Decrease the black and white threshold
		'''
		if self.IMGTHRESH > 10:
			self.IMGTHRESH = self.IMGTHRESH - 10
			return

	def thresh_inc(self):
		'''Increase the black and white threshold
		'''
		if self.IMGTHRESH < 245:
			self.IMGTHRESH = self.IMGTHRESH + 10
			return

	def iso_cyc(self):
		'''Cycle to another ISO settings
		'''
		iso = self.iso
		if iso < 800:
			iso = iso * 2
		else:
			iso = 100
		self.iso = iso
		self.CAMERA.iso = iso
		return iso

	def exp_dec(self):
		'''Decrease the exposure value by 100 units
		'''
		exp = self.get_exp()
		exp = exp - 1000
		self.CAMERA.shutter_speed = exp
		return

	def exp_inc(self):
		'''Increase the exposure value by 100 units
		'''
		exp = self.get_exp()
		exp = exp + 1000
		self.CAMERA.shutter_speed = exp
		return

	def timed_restart(self, start):
		'''This does a few things.
		First it checks the time,
		Every hour or so, it restarts the camera.
		It adds the time to the upper corner of the video frame.
		'''
		now = time.time()
		time_count = now - start
		self.CAMERA.annotate_text = ' ' * 100 + str(int(round(time_count))) + 'sec'
		if time_count > 2*60*60:
			self.CAMERA.stop_recording()
			start = self.start_rec()
		return start

	def stream_cap(self):
		'''Captures a snapshot from the current stream
		'''
		while True:
			self.STREAM.seek(0)
			self.CAMERA.capture(self.STREAM, use_video_port=True, resize=\
				(self.HORDIM, self.VERTDIM), format='jpeg')
			img = Image.open(self.STREAM)
			img.save('/var/tmp/LunAero/tmp.jpg', 'jpeg')
			time.sleep(0.05)
		return
