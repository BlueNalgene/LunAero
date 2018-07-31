#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Just a container for the pin definitions
'''

class RasPiGPIO():
	'''Just a container for the pin definitions
	'''

	import RPi.GPIO as GPIO
	global GPIO

	def __init__(self):
		#GPIO = RPi.GPIO
		global GPIO
		GPIO.setmode(GPIO.BCM)
#		try:
#			GPIO.setmode(GPIO.BCM)
#			GPIO.setwarnings(False)
#			GPIO.setup(5, GPIO.OUT, intial=GPIO.LOW)
#		except RuntimeError:
#			GPIO.cleanup()
#			GPIO = None

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
			GPIO.setup(i, GPIO.OUT)
			if i != self.APINP or self.BPINP:
				GPIO.output(i, GPIO.LOW)
			else:
				GPIO.output(i, GPIO.HIGH)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		global GPIO

		GPIO.cleanup()
