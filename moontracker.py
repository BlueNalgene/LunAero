#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Motor control and recording for Lunaero
Motor A is up and down
Motor B is right and left
'''

from __future__ import print_function

import argparse
import os.path
import time
import traceback
import pygame

from LunCV import Platform
if Platform.platform_detect == 1:
	print("You appear to be running this on a Raspberry Pi")
	from LunCV import CameraCommands as CC
	from LunCV import MotorControl
	MC = MotorControl.MotorControl()
	ONRPI = True
else:
	print("You are not running this on a Raspberry Pi")
	ONRPI = False
	from LunCV import Lclient
	LC = Lclient()

#import matplotlib.pyplot as plt
#import sys
#import subprocess
#from scipy import ndimage

PARSER = argparse.ArgumentParser(\
	description='This is the video recording file for use with LunAero')
PARSER.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',\
	help='display verbose output for debugging')
#PARSER.add_argument('-K', '--Kivy', dest='kivy', default=False, action='store_true',\
	#help='use the Kivy interface (requires external LunAero cell phone app)')
PARSER.add_argument('-c', '--contrast', dest='contrast', default=False, action='store_true',\
	help='brings up a high contrast image while auto-tracking')
PARSER.add_argument('-F', '--force-save', dest='forcesave', default=False, action='store_true',\
	help='forces the video to be saved to /home/pi/Documents for debugging purposes')
ARGS = PARSER.parse_args()

# Definitions used Globally


# Only turn on camera LED if we are in verbose mode.
# Otherwise, just print what you usually would.
if ARGS.verbose:
	print("Starting LunAero moon tracker and video recording platform")
	#if ARGS.kivy:
		#print("Starting LunAero using Kivy controls")
		#print("If you activated this accidentally, use ctrl+c to close")
else:
	if ONRPI:
		pass


def main():
	'''Main
	'''
	from LunCV.Lconfig import RED, BLACK
	prev = 3
	if ONRPI:
		CC.go_prev(prev)
	time.sleep(2)
	if ONRPI:
		exp = CC.get_exp()
	if ARGS.verbose:
		print("exposure speed ", exp)



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

	if ONRPI:
		prev, exp = pygame_centering(prev, exp)

	screen.fill(BLACK)
	pygame.display.update()
	pygame.display.set_caption('Tracking Moon')
	screen.blit(font.render('TRACKING MOON.', True, RED), (25, 25))
	screen.blit(font.render('Click this window and type "q" to quit', True, RED), (25, 75))
	screen.blit(font.render('Or just close this window to to quit.', True, RED), (25, 125))
	screen.blit(font.render('(it might take a few seconds)', True, RED), (25, 175))
	pygame.display.update()

	if ONRPI:
		MC.mot_stop("B")
	else:
		LC.sendout(b'B')

	prev, exp = pygame_tracking(prev, exp)

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
		print("Check that the thumbdrive is plugged in and mounted")
		print("You should see it at /media/pi/MOON1")
		if ARGS.forcesave:
			print("Continuing with a new save location")
			outfile = os.path.join('/home/pi/Documents', outfile)
		else:
			raise ValueError("The thumbdrive is not where I expected it to be!")
	if ARGS.verbose:
		print(str(outfile))
	CC.start_recording(outfile)
	time.sleep(1)
	return start

def pygame_tracking(prev, exp):
	'''Pygame version of the tracking gui
	'''

	from LunCV.Lconfig import IMGTHRESH, VERTTHRESHSTART, HORTHRESHSTART, LOSTRATIO

	start = start_rec()

	cnt = 0
	check = 1
	while cnt < 55:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_z:
					if ONRPI:
						CC.thresh_dec()
					else:
						LC.sendout(b't')
					if ARGS.verbose:
						print("decrease thresholding to ", IMGTHRESH)
				if event.key == pygame.K_x:
					if ONRPI:
						CC.thresh_inc()
					else:
						LC.sendout(b'T')
					if ARGS.verbose:
						print("increase thresholding to ", IMGTHRESH)
				if event.key == pygame.K_q:
					cnt = 100
					if ARGS.verbose:
						print("quitting tracker")
				if event.key == pygame.K_i:
					if ONRPI:
						iso = CC.iso_cyc()
					else:
						LC.sendout(b'i')
					print("iso set to ", iso)
				if event.key == pygame.K_d:
					if ONRPI:
						CC.exp_dec()
					else:
						LC.sendout(b'e')
					print("exposure time set to ", exp)
				if event.key == pygame.K_b:
					if ONRPI:
						CC.exp_inc()
					else:
						LC.sendout(b'E')
					print("exposure time set to ", exp)
				if event.key == pygame.K_v:
					prev = prev + 1
					if prev > 5:
						prev = 1
						CC.stop_preview()
					CC.go_prev(prev)
			if event.type == pygame.QUIT:
				cnt = 100
		start = CC.timed_restart(start)

		if ONRPI:
			diffx, diffy, ratio, cmx, cmy = CC.get_img()
			if ARGS.verbose:
				print(ratio, cmx, cmy, diffx, diffy)

			if (abs(diffy) > VERTTHRESHSTART or abs(diffx) > HORTHRESHSTART):
				check = CC.checkandmove()

			lost_count = 0
			if check == 1:       #Moon successfully centered
				if ARGS.verbose:
					print("centered")
				lost_count = 0
				img = CC.stream_cap()
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

	cnt = 0
	while cnt < 10:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				if ONRPI:
					if ONRPI:
						MC.mot_stop("B")
					else:
						LC.sendout(b'B')
				else:
					LC.sendout(b'B')
				cnt = 100
			# check if key is pressed
			# if you use event.key here it will give you error at runtime
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					if ARGS.verbose:
						print("left")
					if ONRPI:
						MC.mot_left()
					else:
						LC.sendout(b'a')
				if event.key == pygame.K_RIGHT:
					if ARGS.verbose:
						print("right")
					if ONRPI:
						MC.mot_right()
					else:
						LC.sendout(b'd')
				if event.key == pygame.K_UP:
					if ARGS.verbose:
						print("up")
					if ONRPI:
						MC.mot_up()
					else:
						LC.sendout(b'w')
				if event.key == pygame.K_DOWN:
					if ARGS.verbose:
						print("down")
					if ONRPI:
						MC.mot_down()
					else:
						LC.sendout(b's')
				if event.key == pygame.K_SPACE:
					if ARGS.verbose:
						print("stop")
					if ONRPI:
						MC.mot_stop("B")
					else:
						LC.sendout(b'B')
				if event.key == pygame.K_i:
					if ONRPI:
						iso = CC.iso_cyc()
					else:
						LC.sendout(b'i')
					print("iso set to ", iso)
				if event.key == pygame.K_d:
					if ONRPI:
						CC.exp_dec()
					else:
						LC.sendout(b'e')
					print("exposure time set to ", exp)
				if event.key == pygame.K_b:
					if ONRPI:
						CC.exp_inc()
					else:
						LC.sendout(b'E')
					print("exposure time set to ", exp)
				if event.key == pygame.K_v:
					prev = prev + 1
					if prev > 5:
						prev = 1
					CC.stop_preview()
					CC.go_prev(prev)
				if event.key == pygame.K_r:
					if ARGS.verbose:
						print("run tracker")
					if ONRPI:
						MC.mot_stop("B")
					else:
						LC.sendout(b'B')
					cnt = 100
				if event.key == pygame.K_RETURN:
					if ARGS.verbose:
						print("run tracker")
					if ONRPI:
						MC.mot_stop("B")
					else:
						LC.sendout(b'B')
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
		print("Exception Type: ", type(inst))
		print("Exception Args: ", inst.args)
		print("Exception     : ", inst)
		traceback.print_exc()
	finally:
		time.sleep(2)
		if ONRPI:
			CC.shutdown_camera()
		os.system("killall gpicview")  #remove pics from screen if there are any
		pygame.quit()
