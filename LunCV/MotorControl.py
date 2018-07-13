#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''MotorControl Module
'''

import time

import RPi.GPIO as GPIO

from . import RasPiGPIO

class MotorControl():
	'''This class defines the different motions available to the LunAero hardware
	'''

	RPG = RasPiGPIO()

	freq = 1000
	pwma = GPIO.PWM(RPG.APINP, freq)
	pwmb = GPIO.PWM(RPG.BPINP, freq)
	dca = 0
	dcb = 0

	def __init__(self):
		'''Initialize PWM on pwm pins,
		Set duty cycle variables to 0 and pulse at that duty cycle
		'''
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
			GPIO.output(RPG.APIN1, GPIO.LOW)
			GPIO.output(RPG.APIN2, GPIO.LOW)
			GPIO.output(RPG.BPIN1, GPIO.LOW)
			GPIO.output(RPG.BPIN2, GPIO.LOW)
		if direct == "Y":
			while self.dca > 0:
				self.dca = self.dca - 1
				self.pwma.ChangeDutyCycle(self.dca)
				time.sleep(.01)
			GPIO.output(RPG.APIN1, GPIO.LOW)
			GPIO.output(RPG.APIN2, GPIO.LOW)
		if direct == "X":
			while self.dcb > 0:
				self.dcb = self.dcb - 1
				self.pwmb.ChangeDutyCycle(self.dcb)
				time.sleep(.01)
			GPIO.output(RPG.BPIN1, GPIO.LOW)
			GPIO.output(RPG.BPIN2, GPIO.LOW)
		return

	def mot_up(self):
		'''Move up
		'''
		print("moving up")
		GPIO.output(RPG.APIN1, GPIO.HIGH)
		GPIO.output(RPG.APIN2, GPIO.LOW)
		#GPIO.output(RPG.APINP, GPIO.HIGH)
		return

	def mot_down(self):
		'''Move down
		'''
		print("moving down")
		GPIO.output(RPG.APIN1, GPIO.LOW)
		GPIO.output(RPG.APIN2, GPIO.HIGH)
		#GPIO.output(RPG.APINP, GPIO.HIGH)
		return

	def mot_left(self):
		'''Move left
		'''
		print("moving left")
		GPIO.output(RPG.BPIN1, GPIO.HIGH)
		GPIO.output(RPG.BPIN2, GPIO.LOW)
		#GPIO.output(RPG.BPINP, GPIO.HIGH)
		return

	def mot_right(self):
		'''Move right
		'''
		print("moving right")
		GPIO.output(RPG.BPIN1, GPIO.LOW)
		GPIO.output(RPG.BPIN2, GPIO.HIGH)
		#GPIO.output(RPG.BPINP, GPIO.HIGH)
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
