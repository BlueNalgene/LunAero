#!/bin/usr/python3

'''This is the frontend for an experimental version of the analysis
Run on a normal computer, not the RasPi
'''

from __future__ import print_function
import time
import pygame
import cv2
from PIL import Image

from LunCV import Manipulations

SIZE = [1280, 810]
SCREEN = pygame.display.set_mode(SIZE)

def main():
	'''This is the main function
	It activates the Pygame interface and calls other things
	'''
	display_color = (255, 0, 0)
	background_color = (30, 30, 30)
	pygame.init()
	pygame.display.set_caption('Manual control')
	font = pygame.font.SysFont('Arial', 25)
	SCREEN.fill(background_color)
	SCREEN.blit(font.render('Press ENTER or r to run', True, display_color), (25, 25))
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

	SCREEN.fill(background_color)
	pygame.display.update()
	pygame.display.set_caption('Tracking Moon')
	SCREEN.blit(font.render('Space = Pause, f = FRAME', True, display_color), (25, 25))
	SCREEN.blit(font.render('Click this window and type "q" to quit', True, display_color), (25, 75))
	pygame.display.update()

	pos_frame = 0

	while status_flag:
		pygame.draw.rect(SCREEN, background_color, (25, 780, 380, 25), 0)
		SCREEN.blit(font.render('Frame Number:', True, display_color), (25, 780))
		SCREEN.blit(font.render(str(pos_frame), True, display_color), (200, 780))
		frame, result = runner(pos_frame)
		frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
		result = pygame.image.frombuffer(result.tostring(), result.shape[1::-1], "RGB")
		frame = pygame.transform.scale(frame, (720, 405))
		result = pygame.transform.scale(result, (720, 405))
		SCREEN.blit(frame, (560, 0))
		SCREEN.blit(result, (560, 405))
		pygame.draw.rect(SCREEN, display_color, (560, 0, 720, 405), 2)
		pygame.draw.rect(SCREEN, display_color, (560, 405, 720, 405), 2)
		for i in range(560, 1280, 20):
			pygame.draw.line(SCREEN, display_color, [i, 405], [i, 810], 1)
		for i in range(405, 810, 20):
			pygame.draw.line(SCREEN, display_color, [560, i], [1280, i], 1)
		pygame.draw.line(SCREEN, display_color, [920, 405], [920, 810], 3)
		pygame.draw.line(SCREEN, display_color, [560, 606], [1280, 606], 4)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				status_flag = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pos_frame = frame_cycle()
					pos_frame = int(pos_frame) - 1
				if event.key == pygame.K_q:
					status_flag = False
				if event.key == pygame.K_SPACE:
					pause_cycle()
		pygame.display.update()
		pos_frame = pos_frame + 1
	print("Program ended on frame ", str(pos_frame))

def runner(pos_frame):
	'''Runs the script with appropriate manipulation
	'''
	#CAP = cv2.VideoCapture('/home/wes/Documents/alt/Migrants.mp4')
	#### IT IS ABOUT 132000 FRAMES
	CAP = cv2.VideoCapture('/media/wes/ExtraDrive1/1524943548outA.mp4')
	CAP.set(cv2.CAP_PROP_POS_FRAMES, pos_frame)
	ret, frame = CAP.read()

	if ret:
		#print("Frame ", pos_frame)
		LCV = Manipulations()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (5, 5), 0)
		lower_thresh, upper_thresh = LCV.magic_thresh(gray)
		contours = LCV.cv_contour(gray, lower_thresh, upper_thresh)
		ellipse, result = LCV.center_moon(frame, contours)
		result = LCV.subtract_background(result)
		result = LCV.halo_noise(ellipse, result)
		contours = LCV.cv_contour(result, 0, 255)
		size_list, centers = LCV.cntsize(contours)
		result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
		for i in range(0, len(size_list)):
			cv2.circle(result, (int(centers[i][0]), int(centers[i][1])), int(size_list[i]/2), (255, 0, 255), 2)
			print(pos_frame, ",", centers[i][0][0], ",", centers[i][1][0], ",", size_list[i])
		##cv2.imwrite('current.png', frame)
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

def pause_cycle():
	time.sleep(0.1)
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				status_flag = False
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					return
				if event.key == pygame.K_q:
					return

def frame_cycle():
	time.sleep(0.1)
	font = pygame.font.SysFont('Arial', 25)
	display_color = (255, 0, 0)
	background_color = (30, 30, 30)
	text = ""
	while True:
		pygame.draw.rect(SCREEN, background_color, (25, 125, 200, 200), 0)
		SCREEN.blit(font.render('Jump to FRAME:', True, display_color), (25, 125))
		SCREEN.blit(font.render(text, True, display_color), (50, 175))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				status_flag = False
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					pygame.draw.rect(SCREEN, background_color, (25, 125, 400, 200), 0)
					pygame.display.update()
					return text
				elif event.key == pygame.K_BACKSPACE:
					text = text[:-1]
				else:
					text += event.unicode

if __name__ == '__main__':
	main()
	pygame.quit()
