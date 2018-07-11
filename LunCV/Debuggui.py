#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''This module provides the gui information for running the experimental.py file
It is enabled there and called up to provide a gui for debugging and hunting bird contours.
'''
import time
import pygame

class Gui():
	'''Begin class
	'''
	# Pygame settings
	pygame.init()
	SCREEN = [1280, 810]
	SCREEN = pygame.display.set_mode(SCREEN) #Don't touch this line.
	DISPLAY_COLOR = (255, 0, 0)
	BACKGROUND_COLOR = (30, 30, 30)
	FONT = pygame.font.SysFont('Arial', 25)

	def __init__(self):
		'''Null
		'''

	def initialize_gui(self, status_flag):
		'''It activates the Pygame interface and calls other things
		'''
		pygame.display.set_caption('Manual control')
		self.SCREEN.fill(self.BACKGROUND_COLOR)
		self.SCREEN.blit(self.FONT.render('Press ENTER or r to run', True, self.DISPLAY_COLOR), (25, 25))
		pygame.display.update()

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
						print("run grid tracker")
						status_flag = True
					if event.key == pygame.K_RETURN:
						print("run grid tracker")
						status_flag = True

		self.SCREEN.fill(self.BACKGROUND_COLOR)
		pygame.display.update()
		pygame.display.set_caption('Tracking Moon')
		self.SCREEN.blit(self.FONT.render('Space = Pause, f = FRAME', True, self.DISPLAY_COLOR), (25, 25))
		self.SCREEN.blit(self.FONT.render('Click this window and type "q" to quit', True, \
			self.DISPLAY_COLOR), (25, 75))
		pygame.display.update()
		return status_flag

	def frame_number(self, pos_frame):
		'''Just tells you what frame you are on in the gui
		'''
		pygame.draw.rect(self.SCREEN, self.BACKGROUND_COLOR, (25, 780, 380, 25), 0)
		self.SCREEN.blit(self.FONT.render('Frame Number:', True, self.DISPLAY_COLOR), (25, 780))
		self.SCREEN.blit(self.FONT.render(str(pos_frame), True, self.DISPLAY_COLOR), (200, 780))

	def frame_display(self, pos_frame, frame, result):
		'''This displays the two frames we have calculated,
		our original and the modified frame.  It also puts a grid
		over the modified frame for easier location estimation.
		Grid lines are spaced 54 pix apart.
		'''
		status_flag = True
		frame = pygame.image.frombuffer(frame.tostring(), frame.shape[1::-1], "RGB")
		result = pygame.image.frombuffer(result.tostring(), result.shape[1::-1], "RGB")
		frame = pygame.transform.scale(frame, (720, 405))
		result = pygame.transform.scale(result, (720, 405))
		self.SCREEN.blit(frame, (560, 0))
		self.SCREEN.blit(result, (560, 405))
		pygame.draw.rect(self.SCREEN, self.DISPLAY_COLOR, (560, 0, 720, 405), 2)
		pygame.draw.rect(self.SCREEN, self.DISPLAY_COLOR, (560, 405, 720, 405), 2)
		for i in range(560, 1280, 20):
			pygame.draw.line(self.SCREEN, self.DISPLAY_COLOR, [i, 405], [i, 810], 1)
		for i in range(405, 810, 20):
			pygame.draw.line(self.SCREEN, self.DISPLAY_COLOR, [560, i], [1280, i], 1)
		pygame.draw.line(self.SCREEN, self.DISPLAY_COLOR, [920, 405], [920, 810], 3)
		pygame.draw.line(self.SCREEN, self.DISPLAY_COLOR, [560, 606], [1280, 606], 4)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				status_flag = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_f:
					pos_frame = frame_cycle(self)
					pos_frame = int(pos_frame) - 1
				if event.key == pygame.K_q:
					status_flag = False
				if event.key == pygame.K_SPACE:
					pause_cycle()
		pygame.display.update()
		return pos_frame, status_flag

def pause_cycle():
	'''This pauses the program until unpaused
	'''
	time.sleep(0.1)
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					return
				if event.key == pygame.K_q:
					return

def frame_cycle(self):
	'''This allows us the pick the frame we want to start on
	'''
	time.sleep(0.1)
	text = ""
	while True:
		pygame.draw.rect(self.SCREEN, self.BACKGROUND_COLOR, (25, 125, 200, 200), 0)
		self.SCREEN.blit(self.FONT.render('Jump to FRAME:', True, self.DISPLAY_COLOR), (25, 125))
		self.SCREEN.blit(self.FONT.render(text, True, self.DISPLAY_COLOR), (50, 175))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return text
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					pygame.draw.rect(self.SCREEN, self.BACKGROUND_COLOR, (25, 125, 400, 200), 0)
					pygame.display.update()
					return text
				elif event.key == pygame.K_BACKSPACE:
					text = text[:-1]
				else:
					text += event.unicode
