#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Motor control and recording for Lunaero
Motor A is up and down
Motor B is right and left
'''

from __future__ import print_function

import argparse
import threading
import time
import traceback
import pygame

from LunAeroClient import Lclient
LC = Lclient.Lclient()

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
	#TODO function to pull prev from the go function
	prev = 3
	prev = LC.sendrecv(b'p:')
	print(prev)
	time.sleep(2)

	pygame.init()

	prev = pygame_centering(prev)
	LC.sendout(b'B:')
	prev = pygame_tracking(prev)


def start_rec():
	'''Starts recording, and starts timer
	'''

	start = time.time()
	LC.sendout(b'x:')
	if ARGS.verbose:
		print("Preparing outfile from time ", start)
	return start

def pygame_tracking(prev):
	'''Pygame version of the tracking gui
	'''

	size = [1080, 720]
	screen = pygame.display.set_mode(size)
	tracker_info()
	pygame.display.update()

	start = start_rec()

	cnt = False
	while cnt == False:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_z:
					LC.sendout(b't:')
					if ARGS.verbose:
						print("decrease thresholding to ", IMGTHRESH)
				if event.key == pygame.K_x:
					LC.sendout(b'T:')
					if ARGS.verbose:
						print("increase thresholding to ", IMGTHRESH)
				if event.key == pygame.K_q:
					cnt = True
					if ARGS.verbose:
						print("quitting tracker")
				if event.key == pygame.K_i:
					iso = LC.sendrecv(b'i:')
					print("iso set to ", iso)
				if event.key == pygame.K_e:
					if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
						LC.sendout(b'E:')
					else:
						LC.sendout(b'e:')
				if event.key == pygame.K_p:
					LC.sendout(b'P:')
			if event.type == pygame.QUIT:
				cnt = True

		LC.sendrecv(b'A:')
		img = pygame.image.load('tmp.jpg').convert()
		rect = pygame.Rect(50, 200, 640, 480)
		screen.blit(img, rect)
		pygame.display.update(rect)

		conf = LC.sendrecv(b'r:')
		if conf == '1':
			start = str(start)
			start = 'z' + start + ':'
			start = bytes(start, encoding='UTF-8')
			start = LC.sendrecv(start)

		conf = LC.sendrecv(b'R:')
		if conf == 1:
			print("close loop")
			cnt = True
		else:
			print("again!")

	return prev

def pygame_centering(prev):
	''' Pygame based interface for centering the moon
	'''

	cnt = False
	size = [1080, 720]
	screen = pygame.display.set_mode(size)
	center_info()
	pygame.display.update()
	while cnt == False:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				LC.sendout(b'B:')
				cnt = True
			# check if key is pressed
			# if you use event.key here it will give you error at runtime
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					if ARGS.verbose:
						print("left")
					LC.sendout(b'a:')
				if event.key == pygame.K_RIGHT:
					if ARGS.verbose:
						print("right")
					LC.sendout(b'd:')
				if event.key == pygame.K_UP:
					if ARGS.verbose:
						print("up")
					LC.sendout(b'w:')
				if event.key == pygame.K_DOWN:
					if ARGS.verbose:
						print("down")
					LC.sendout(b's:')
				if event.key == pygame.K_SPACE:
					if ARGS.verbose:
						print("stop")
					LC.sendout(b'B:')
				if event.key == pygame.K_i:
					iso = LC.sendrecv(b'i:')
					print("iso set to ", iso)
				if event.key == pygame.K_e:
					if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
						LC.sendout(b'E:')
					else:
						LC.sendout(b'e:')
				if event.key == pygame.K_p:
					LC.sendout(b'P:')
				if event.key == pygame.K_r:
					if ARGS.verbose:
						print("run tracker")
					LC.sendout(b'B:')
					cnt = True
				if event.key == pygame.K_RETURN:
					if ARGS.verbose:
						print("run tracker")
					LC.sendout(b'B:')
					cnt = True
		LC.sendrecv(b'A:')
		img = pygame.image.load('tmp.jpg').convert()
		rect = pygame.Rect(50, 200, 640, 480)
		screen.blit(img, rect)
		pygame.display.update(rect)
	if ARGS.verbose:
		print("quitting manual control, switching to tracking")
	return prev

def center_info():
	from LunAeroClient.Lconfig import RED, BLACK

	pygame.display.set_caption('Manual control')
	size = [1080, 720]
	screen = pygame.display.set_mode(size)
	font = pygame.font.SysFont('Arial', 25)
	screen.blit(font.render('Use arrow keys to move.', True, RED), (25, 25))
	screen.blit(font.render('Hit the space bar to stop.', True, RED), (25, 60))
	screen.blit(font.render('Options: (i)so, (e)xposure down, (E)xposure up, (p).', True, RED), (25, 95))
	screen.blit(font.render('Press ENTER or r to run the', True, RED), (25, 130))
	screen.blit(font.render('moon tracker', True, RED), (25, 165))
	return

def tracker_info():
	from LunAeroClient.Lconfig import RED, BLACK

	pygame.display.set_caption('Automatic Tracking')
	size = [1080, 720]
	screen = pygame.display.set_mode(size)
	font = pygame.font.SysFont('Arial', 25)
	screen.fill(BLACK)
	pygame.display.set_caption('Tracking Moon')
	screen.blit(font.render('TRACKING MOON.', True, RED), (25, 25))
	screen.blit(font.render('Click this window and type "q" to quit', True, RED), (25, 75))
	screen.blit(font.render('Or just close this window to to quit.', True, RED), (25, 125))
	screen.blit(font.render('(it might take a few seconds)', True, RED), (25, 175))
	return

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
