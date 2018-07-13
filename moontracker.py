#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Motor control and recording for Lunaero
Motor A is up and down
Motor B is right and left
'''

from __future__ import print_function

import argparse
import io
import os
import os.path
import time
import numpy as np
import pygame
from PIL import Image

import picamera

from LunCV import RasPiGPIO
from LunCV import MotorControl

#import matplotlib.pyplot as plt
#import sys
#import subprocess
#from scipy import ndimage

PARSER = argparse.ArgumentParser(\
	description='This is the video recording file for use with LunAero')
PARSER.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',\
	help='display verbose output for debugging')
PARSER.add_argument('-K', '--Kivy', dest='kivy', default=False, action='store_true',\
	help='use the Kivy interface (requires external LunAero cell phone app)')
PARSER.add_argument('-c', '--contrast', dest='contrast', default=False, action='store_true',\
	help='brings up a high contrast image while auto-tracking')
PARSER.add_argument('-F', '--force-save', dest='forcesave', default=False, action='store_true',\
	help='forces the video to be saved to /home/pi/Documents for debugging purposes')
ARGS = PARSER.parse_args()

# Definitions used Globally
MC = MotorControl()
RPG = RasPiGPIO()
CAMERA = picamera.PiCamera()
STREAM = io.BytesIO()
GPIO = RasPiGPIO()

# Only turn on camera LED if we are in verbose mode.
# Otherwise, just print what you usually would.
if ARGS.verbose:
	print("Starting LunAero moon tracker and video recording platform")
	if ARGS.kivy:
		print("Starting LunAero using Kivy controls")
		print("If you activated this accidentally, use ctrl+c to close")
else:
	CAMERA.led = False


def main():
	'''Main
	'''
	from __init__ import RED, BLACK

	CAMERA.video_stabilization = True
	CAMERA.resolution = (1920, 1080)
	CAMERA.color_effects = (128, 128) # turn camera to black and white
	prev = 3
	go_prev(prev)
	time.sleep(2)

	exp = CAMERA.exposure_speed
	if ARGS.verbose:
		print("exposure speed ", exp)


	if ARGS.kivy:
		pass
	else:
		pygame.init()
		pygame.display.set_caption('Manual control')
		size = [400, 240]
		screen = pygame.display.set_mode(size)
		font = pygame.font.SysFont('Arial', 25)
		screen.blit(font.render('Use arrow keys to move.', True, RED), (25, 25))
		screen.blit(font.render('Hit the space bar to stop.', True, RED), (25, 75))
		screen.blit(font.render('Press ENTER or r to run the', True, RED), (25, 125))
		screen.blit(font.render('moon tracker', True, RED), (25, 165))
		pygame.display.update()

	if ARGS.kivy:
		pass
	else:
		prev, exp = pygame_centering(prev, exp)

	if ARGS.kivy:
		pass
	else:
		screen.fill(BLACK)
		pygame.display.update()
		pygame.display.set_caption('Tracking Moon')
		screen.blit(font.render('TRACKING MOON.', True, RED), (25, 25))
		screen.blit(font.render('Click this window and type "q" to quit', True, RED), (25, 75))
		screen.blit(font.render('Or just close this window to to quit.', True, RED), (25, 125))
		screen.blit(font.render('(it might take a few seconds)', True, RED), (25, 175))
		pygame.display.update()

	MC.mot_stop("B")

	if ARGS.kivy:
		pass
	else:
		prev, exp = pygame_tracking(prev, exp)

#def kivy_tracking(prev, exp):
	#'''Kivy version of the tracking gui
	#Takes screeshots from video stream
	#'''

	#from __init__ import IMGTHRESH, VERTTHRESHSTART, HORTHRESHSTART, LOSTRATIO

	#start = start_rec()

def get_img():
	'''Capture an image and see how close it is to center
	'''
	from __init__ import IMGTHRESH, HORDIM, VERTDIM, CENX, CENY

	# Capture image and convert to monochrome np array
	CAMERA.capture(STREAM, use_video_port=True, resize=(HORDIM, VERTDIM), format='jpeg')
	img = Image.open(STREAM)
	img = img.convert('L')
	img = img.point(lambda x: 0 if x < IMGTHRESH else 255, '1')
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
	ratio = img.sum()/(HORDIM*VERTDIM)

	# Determines the difference of the center of mass from the center of the frame.
	# For x: if positive, shift right; if negative, shift left
	# For y: if positive, shift down; if negative, shift up
	diffx = CENX - cmx
	diffy = CENY - cmy
	if ARGS.verbose:
		print(ratio, cmx, cmy, diffx, diffy)
	return diffx, diffy, ratio

def checkandmove():
	'''This checks the difference in thresholds
	'''
	from __init__ import LOSTRATIO, HORTHRESHSTOP, VERTTHRESHSTOP

	diffx, diffy, ratio = get_img()
	if ratio < LOSTRATIO:
		# Default to 'moon is lost'
		rtn = 2
	else:
		if abs(diffx) > HORTHRESHSTOP:
			if diffx > 0:
				MC.mot_left()
			else:
				MC.mot_right()
			MC.speed_up("X")
		if abs(diffy) > VERTTHRESHSTOP:
			if diffy > 0:
				MC.mot_up()
			else:
				MC.mot_down()
			MC.speed_up("Y")
		if (abs(diffx) < HORTHRESHSTOP and MC.dcB > 0):
			MC.mot_stop("X")
		if (abs(diffy) < VERTTHRESHSTOP and MC.dcA > 0):
			MC.mot_stop("Y")
		if (abs(diffx) < HORTHRESHSTOP and abs(diffy) < VERTTHRESHSTOP):
			MC.mot_stop("B")
			rtn = 1
		else:
			rtn = 0
	return rtn


def start_rec():
	'''Starts recording, and starts timer
	'''

	start = time.time()
	if ARGS.verbose:
		print(start)
		print("Preparing outfile")
	outfile = int(time.time())
	outfile = str(outfile) + 'outA.h264'
	if os.path.isdir('/media/pi/MOON1'):
		outfile = os.path.join('/media/pi/MOON1', outfile)
	else:
		print("----Error-----")
		print("Check that the thumbdrive is plugged in and mounted")
		print("You should see it at /media/pi/MOON1")
		if ARGS.forcesave:
			outfile = os.path.join('/home/pi/Documents', outfile)
		else:
			raise ValueError("The thumbdrive is not where I expected it to be!")
	if ARGS.verbose:
		print(str(outfile))
	CAMERA.start_recording(outfile)
	time.sleep(1)
	return start

def go_prev(prev):
	'''Preview size options
	'''

	if prev == 1:
		CAMERA.start_preview(fullscreen=False, window=(1200, -20, 640, 480))
	if prev == 2:
		CAMERA.start_preview(fullscreen=False, window=(800, -20, 1280, 960))
	if prev == 3:
		CAMERA.start_preview(fullscreen=False, window=(20, 400, 640, 480))
	if prev == 4:
		CAMERA.start_preview(fullscreen=False, window=(20, 200, 1280, 960))
	if prev == 5:
		CAMERA.start_preview(fullscreen=True)
	return

def pygame_tracking(prev, exp):
	'''Pygame version of the tracking gui
	'''

	from __init__ import IMGTHRESH, VERTTHRESHSTART, HORTHRESHSTART, LOSTRATIO

	start = start_rec()

	cnt = 0
	while cnt < 55:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_z:
					if IMGTHRESH > 10:
						IMGTHRESH = (IMGTHRESH - 10)
					if ARGS.verbose:
						print("decrease thresholding to ", IMGTHRESH)
				if event.key == pygame.K_x:
					if IMGTHRESH < 245:
						IMGTHRESH = (IMGTHRESH + 10)
					if ARGS.verbose:
						print("increase thresholding to ", IMGTHRESH)
				if event.key == pygame.K_q:
					cnt = 100
					if ARGS.verbose:
						print("quitting tracker")
				if event.key == pygame.K_i:
					iso = CAMERA.iso()
					if iso < 800:
						iso = iso * 2
					else:
						iso = 100
					CAMERA.iso = iso
					print("iso set to ", iso)
				if event.key == pygame.K_d:
					exp = exp - 100
					CAMERA.shutter_speed = exp
					print("exposure time set to ", exp)
				if event.key == pygame.K_b:
					exp = exp + 100
					CAMERA.shutter_speed = exp
					print("exposure time set to ", exp)
				if event.key == pygame.K_v:
					prev = prev + 1
					if prev > 5:
						prev = 1
					CAMERA.stop_preview()
					go_prev(prev)
			if event.type == pygame.QUIT:
				cnt = 100
		now = time.time()      #check the time to restart camera every hour or so
		time_count = now - start
		CAMERA.annotate_text = ' ' * 100 + str(int(round(time_count))) + 'sec'
		if time_count > 2*60*60:
			if ARGS.verbose:
				print("restart video")
			CAMERA.stop_recording()
			start = start_rec()
		diffx, diffy, ratio = get_img()
		if (abs(diffy) > VERTTHRESHSTART or abs(diffx) > HORTHRESHSTART):
			check = checkandmove()
		lost_count = 0
		if check == 1:       #Moon successfully centered
			if ARGS.verbose:
				print("centered")
			lost_count = 0
			img = Image.open(STREAM)
			img.save("tmp.png")
			if ARGS.contrast:
				os.system("xdg-open tmp.png") #display image - for debugging only
				time.sleep(3)
				os.system("killall gpicview")
			else:
				pass
		if check == 0:       #centering in progress
			time.sleep(.02)  #sleep for 20ms
		if (check == 2 or ratio < LOSTRATIO):        #moon lost, theshold too low
			lost_count = lost_count + 1
			if ARGS.verbose:
				print("moon lost")
			time.sleep(1)
			if lost_count > 30:
				if ARGS.verbose:
					print("moon totally lost")
				cnt = 100   #set count to 100 to exit the while loop
	return prev, exp

def pygame_centering(prev, exp):
	''' Pygame based interface for centering the moon
	'''

	global CAMERA

	cnt = 0
	while cnt < 10:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				MC.mot_stop("B")
				cnt = 100
			# check if key is pressed
			# if you use event.key here it will give you error at runtime
			if event.type == pygame.KEYDOWN:
				MC.dcA = 100
				MC.dcB = 100
				if event.key == pygame.K_LEFT:
					if ARGS.verbose:
						print("left")
					MC.pwmB.ChangeDutyCycle(MC.dcA)
					MC.mot_left()
				if event.key == pygame.K_RIGHT:
					if ARGS.verbose:
						print("right")
					MC.pwmB.ChangeDutyCycle(MC.dcA)
					MC.mot_right()
				if event.key == pygame.K_UP:
					if ARGS.verbose:
						print("up")
					MC.pwmA.ChangeDutyCycle(MC.dcB)
					MC.mot_up()
				if event.key == pygame.K_DOWN:
					if ARGS.verbose:
						print("down")
					MC.pwmA.ChangeDutyCycle(MC.dcB)
					MC.mot_down()
				if event.key == pygame.K_SPACE:
					if ARGS.verbose:
						print("stop")
					MC.mot_stop("B")
				if event.key == pygame.K_i:
					iso = CAMERA.iso()
					if iso < 800:
						iso = iso * 2
					else:
						iso = 100
					CAMERA.iso = iso
					print("iso set to ", iso)
				if event.key == pygame.K_d:
					exp = exp - 1000
					CAMERA.shutter_speed = exp
					print("exposure time set to ", exp)
				if event.key == pygame.K_b:
					exp = exp + 1000
					CAMERA.shutter_speed = exp
					print("exposure time set to ", exp)
				if event.key == pygame.K_v:
					prev = prev + 1
					if prev > 5:
						prev = 1
					CAMERA.stop_preview()
					go_prev(prev)
				if event.key == pygame.K_r:
					if ARGS.verbose:
						print("run tracker")
					MC.mot_stop("B")
					cnt = 100
				if event.key == pygame.K_RETURN:
					if ARGS.verbose:
						print("run tracker")
					MC.mot_stop("B")
					cnt = 100
	if ARGS.verbose:
		print("quitting manual control, switching to tracking")
	return prev, exp

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		if ARGS.verbose:
			print("keyboard task kill")
	except Exception as inst:
		print(type(inst))
		print(inst.args)
		print(inst)
	finally:
		time.sleep(2)
		MC.mot_stop("B")
		CAMERA.stop_recording()
		os.system("killall gpicview")  #remove pics from screen if there are any
		CAMERA.stop_preview()
		pygame.quit()
		GPIO.cleanup()
