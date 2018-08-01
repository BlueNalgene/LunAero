#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''MotorControl Module
'''

import time

#import RasPiGPIO

class MotorControl():
	'''This class defines the different motions available to the LunAero hardware
	'''

	def __init__(self):
		'''Initialize PWM on pwm pins,
		Set duty cycle variables to 0 and pulse at that duty cycle
		'''
		import RPi.GPIO as GPIO
		self.GPIO = GPIO
		self.GPIO.setmode(self.GPIO.BCM)

		self.APINP = 17  #Pulse width pin for motor A (up and down)
		self.APIN1 = 27  #Motor control - high for up
		self.APIN2 = 22  #Motor control - high for down
		self.BPIN1 = 10  #Motor control - high for left
		self.BPIN2 = 9   #Motor control - high for right
		self.BPINP = 11  #Pulse width pin for motor B (right and left)

		# Setup GPIO and start them with 'off' values
		PINS = (self.APIN1, self.APIN2, self.APINP,\
			self.BPIN1, self.BPIN2, self.BPINP)
		for i in PINS:
			self.GPIO.setup(i, self.GPIO.OUT)
			if i != self.APINP or self.BPINP:
				self.GPIO.output(i, self.GPIO.LOW)
			else:
				self.GPIO.output(i, self.GPIO.HIGH)

		freq = 1000
		self.pwma = self.GPIO.PWM(self.APINP, freq)
		self.pwmb = self.GPIO.PWM(self.BPINP, freq)
		self.dca = 0
		self.dcb = 0

		self.pwma.start(self.dca)
		self.pwmb.start(self.dcb)

	def mot_stop(self, direct):
		'''Stops
		'''
		print("stopping", direct)
		if direct == "B":
			while (self.dca > 0 or self.dcb > 0):
				if self.dca == 100:
					self.dca = 10     #quickly stop motor going full speed
				if self.dcb == 100:
					self.dcb = 10
				if self.dca > 0:
					self.dca = self.dca - 1   #slowly stop motor going slow (tracking moon)
				if self.dcb > 0:
					self.dcb = self.dcb - 1
				self.pwma.ChangeDutyCycle(self.dca)
				self.pwmb.ChangeDutyCycle(self.dcb)
				time.sleep(.005)
			self.GPIO.output(self.RPG.APIN1, self.GPIO.LOW)
			self.GPIO.output(self.RPG.APIN2, self.GPIO.LOW)
			self.GPIO.output(self.RPG.BPIN1, self.GPIO.LOW)
			self.GPIO.output(self.RPG.BPIN2, self.GPIO.LOW)
		if direct == "Y":
			while self.dca > 0:
				self.dca = self.dca - 1
				self.pwma.ChangeDutyCycle(self.dca)
				time.sleep(.01)
			self.GPIO.output(self.RPG.APIN1, self.GPIO.LOW)
			self.GPIO.output(self.RPG.APIN2, self.GPIO.LOW)
		if direct == "X":
			while self.dcb > 0:
				self.dcb = self.dcb - 1
				self.pwmb.ChangeDutyCycle(self.dcb)
				time.sleep(.01)
			self.GPIO.output(self.RPG.BPIN1, self.GPIO.LOW)
			self.GPIO.output(self.RPG.BPIN2, self.GPIO.LOW)
		return

	def mot_up(self):
		'''Move up
		'''
		print("moving up")
		self.pwma.ChangeDutyCycle(100)
		self.GPIO.output(self.RPG.APIN1, self.GPIO.HIGH)
		self.GPIO.output(self.RPG.APIN2, self.GPIO.LOW)
		return

	def mot_down(self):
		'''Move down
		'''
		print("moving down")
		self.pwma.ChangeDutyCycle(100)
		self.GPIO.output(self.RPG.APIN1, self.GPIO.LOW)
		self.GPIO.output(self.RPG.APIN2, self.GPIO.HIGH)
		return

	def mot_left(self):
		'''Move left
		'''
		print("moving left")
		self.pwmb.ChangeDutyCycle(100)
		self.GPIO.output(self.RPG.BPIN1, self.GPIO.HIGH)
		self.GPIO.output(self.RPG.BPIN2, self.GPIO.LOW)
		return

	def mot_right(self):
		'''Move right
		'''
		print("moving right")
		self.pwmb.ChangeDutyCycle(100)
		self.GPIO.output(self.RPG.BPIN1, self.GPIO.LOW)
		self.GPIO.output(self.RPG.BPIN2, self.GPIO.HIGH)
		return

	def speed_up(self, direct):
		'''Increase movement speed
		'''
		if direct == "Y":
			if self.dca < 50:
				self.dca = self.dca + 2
				self.pwma.ChangeDutyCycle(self.dca)
			print("speedup ", direct, self.dca)
		if direct == "X":
			if self.dcb < 50:
				self.dcb = self.dcb + 2
				self.pwmb.ChangeDutyCycle(self.dcb)
			print("speedup", direct, self.dcb)
		return

	def slow_down(self, direct):
		'''Decrease movement speed
		'''
		if direct == "Y":
			if self.dca > 0:
				self.dca = self.dca - 2
				self.pwma.ChangeDutyCycle(self.dca)
			print("slowdown ", direct, self.dca)
		if direct == "X":
			if self.dcb > 0:
				self.dcb = self.dcb - 2
				self.pwmb.ChangeDutyCycle(self.dcb)
			print("slowdown ", direct, self.dcb)
		return
