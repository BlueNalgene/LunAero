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

from LunCV import Lclient
LC = Lclient()

PARSER = argparse.ArgumentParser(\
	description='This is the video recording file for use with LunAero')
PARSER.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',\
	help='display verbose output for debugging')
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

def main():
	'''Main
	'''
	from LunCV.Lconfig import RED, BLACK
	#TODO function to pull prev from the go function
	prev = 3
	prev = LC.sendout(b'p')
	print(prev)
	time.sleep(2)
	exp = 30000
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

	prev, exp = pygame_centering(prev, exp)

	screen.fill(BLACK)
	pygame.display.update()
	pygame.display.set_caption('Tracking Moon')
	screen.blit(font.render('TRACKING MOON.', True, RED), (25, 25))
	screen.blit(font.render('Click this window and type "q" to quit', True, RED), (25, 75))
	screen.blit(font.render('Or just close this window to to quit.', True, RED), (25, 125))
	screen.blit(font.render('(it might take a few seconds)', True, RED), (25, 175))
	pygame.display.update()

	LC.sendout(b'B')

	prev, exp = pygame_tracking(prev, exp)

def start_rec():
	'''Starts recording, and starts timer
	'''

	start = time.time()
	LC.sendout(b'x')
	if ARGS.verbose:
		print("Preparing outfile from time ", start)
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
					LC.sendout(b't')
					if ARGS.verbose:
						print("decrease thresholding to ", IMGTHRESH)
				if event.key == pygame.K_x:
					LC.sendout(b'T')
					if ARGS.verbose:
						print("increase thresholding to ", IMGTHRESH)
				if event.key == pygame.K_q:
					cnt = 100
					if ARGS.verbose:
						print("quitting tracker")
				if event.key == pygame.K_i:
					LC.sendout(b'i')
					print("iso set to ", iso)
				if event.key == pygame.K_d:
					LC.sendout(b'e')
					print("exposure time set to ", exp)
				if event.key == pygame.K_b:
					LC.sendout(b'E')
					print("exposure time set to ", exp)
				if event.key == pygame.K_v:
					LC.sendout(b'P')
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
				LC.sendout(b'B')
				cnt = 100
			# check if key is pressed
			# if you use event.key here it will give you error at runtime
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					if ARGS.verbose:
						print("left")
					LC.sendout(b'a')
				if event.key == pygame.K_RIGHT:
					if ARGS.verbose:
						print("right")
					LC.sendout(b'd')
				if event.key == pygame.K_UP:
					if ARGS.verbose:
						print("up")
					LC.sendout(b'w')
				if event.key == pygame.K_DOWN:
					if ARGS.verbose:
						print("down")
					LC.sendout(b's')
				if event.key == pygame.K_SPACE:
					if ARGS.verbose:
						print("stop")
					LC.sendout(b'B')
				if event.key == pygame.K_i:
					LC.sendout(b'i')
					print("iso set to ", iso)
				if event.key == pygame.K_d:
					LC.sendout(b'e')
					print("exposure time set to ", exp)
				if event.key == pygame.K_b:
					LC.sendout(b'E')
					print("exposure time set to ", exp)
				if event.key == pygame.K_v:
					LC.sendout(b'P')
				if event.key == pygame.K_r:
					if ARGS.verbose:
						print("run tracker")
					LC.sendout(b'B')
					cnt = 100
				if event.key == pygame.K_RETURN:
					if ARGS.verbose:
						print("run tracker")
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
		pygame.quit()
