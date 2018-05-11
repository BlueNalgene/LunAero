#!/bin/usr/python3

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi
'''

from __future__ import print_function
import pygame
import cv2
from PIL import Image

from LunCV import Manipulations as LCV

def main():
	'''This is the main function
	It activates the Pygame interface and calls other things
	'''
	red = (255, 0, 0)
	black = (0, 0, 0)
	pygame.init()
	pygame.display.set_caption('Manual control')
	size = [1280, 768]
	screen = pygame.display.set_mode(size)
	font = pygame.font.SysFont('Arial', 25)
	screen.blit(font.render('Press x to select the file to run', True, red), (25, 25))
	screen.blit(font.render('Hit the space bar to stop.', True, red), (25, 75))
	screen.blit(font.render('Press ENTER or r to run the', True, red), (25, 125))
	screen.blit(font.render('moon tracker', True, red), (25, 165))
	pygame.display.update()
	status_flag = False

	while not status_flag:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				status_flag = True
			# check if key is pressed
			# if you use event.key here it will give you error at runtime
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					print("left")
				if event.key == pygame.K_RIGHT:
					print("right")
				if event.key == pygame.K_UP:
					print("up")
				if event.key == pygame.K_DOWN:
					print("down")
				if event.key == pygame.K_SPACE:
					print("space")
				if event.key == pygame.K_r:
					print("run tracker")
					status_flag = True
				if event.key == pygame.K_RETURN:
					print("run tracker")
					status_flag = True
	print("quitting manual control, switching to tracking")

	screen.fill(black)
	pygame.display.update()
	pygame.display.set_caption('Tracking Moon')
	screen.blit(font.render('TRACKING MOON.', True, red), (25, 25))
	screen.blit(font.render('Click this window and type "q" to quit', True, red), (25, 75))
	screen.blit(font.render('Or just close this window to to quit.', True, red), (25, 125))
	screen.blit(font.render('(it might take a few seconds)', True, red), (25, 175))
	pygame.display.update()

	pos_frame = 0

	while status_flag:
		if event.key == pygame.K_r:
			status_flag = False
		print("1")
		frame, result = runner(pos_frame)
		#frame = Image.fromarray(frame)
		#result = Image.fromarray(result)
		print("2")
		frame = pygame.surfarray.make_surface(frame)
		result = pygame.surfarray.make_surface(result)
		frame = pygame.transform.scale(frame, (700, 500))
		print("3")
		result = pygame.transform.scale(result, (700, 500))
		print("4")
		screen.blit(frame, (580, 0))
		print("5")
		screen.blit(result, (580, 500))
		print("6")
		pygame.display.update()
		print("7")
		pos_frame = pos_frame + 1
		print("8")

def runner(pos_frame):
	'''Runs the script with appropriate manipulation
	'''
	CAP = cv2.VideoCapture('/home/wes/Documents/alt/Migrants.mp4')
	print("1.1")
	CAP.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
	ret, frame = CAP.read()
	print("1.3")
	#while CAP.isOpened():
		#pos_frame = CAP.get(cv2.CAP_PROP_POS_FRAMES)
		#print("1.2")
		#ret, frame = CAP.read()
		#print("1.3")

	if ret:
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (5, 5), 0)
		print("1.4")
		lower_thresh, upper_thresh = LCV.magic_thresh(gray)
		print("1.5")
		contours = LCV.cv_contour(gray, lower_thresh, upper_thresh)
		print("1.6")
		result = LCV.center_moon(frame, contours)
		print("1.7")
		result = LCV.subtract_background(result)
		print("1.8")
		cv2.imwrite('current.png', frame)
		print("1.9")
		return frame, result
		# This mess displays different things side by side
		# The Mother window shows the manipulated image that is being used for cakculations
		# The Original window shows the contours overlaid on the original frame
		#cv2.namedWindow("Mother", cv2.WINDOW_NORMAL)
		#cv2.resizeWindow("Mother", 700, 500)
		#cv2.imshow("Mother", result)
		#cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
		#cv2.resizeWindow("Original", 700, 500)
		#cv2.imshow("Original", frame)

		#if contours:
			#result = cv2.morphologyEx(result, cv2.MORPH_OPEN, MATTWO)
			##result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
			#cv2.drawContours(result, contours, -1, (255, 255, 255), 2)
		#cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
		#cv2.resizeWindow("Test", 700, 500)
		#cv2.imshow("Test", result)
	#else:
		## The next frame is not ready, so we try to read it again
		#CAP.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1)
		#print("frame is not ready")
		## It is better to wait for a while for the next frame to be ready
		#cv2.waitKey(1000)

	#if cv2.waitKey(10) & 0xFF == ord('q'):
			#return

if __name__ == '__main__':
	main()
	pygame.quit()
