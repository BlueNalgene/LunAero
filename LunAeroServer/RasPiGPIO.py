#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

'''Just a container for the pin definitions
'''

class RasPiGPIO():
	'''Just a container for the pin definitions
	'''

	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	APINP = 17  #Pulse width pin for motor A (up and down)
	APIN1 = 27  #Motor control - high for up
	APIN2 = 22  #Motor control - high for down
	BPIN1 = 10  #Motor control - high for left
	BPIN2 = 9   #Motor control - high for right
	BPINP = 11  #Pulse width pin for motor B (right and left)

	# Setup GPIO and start them with 'off' values
	PINS = (APIN1, APIN2, APINP, BPIN1, BPIN2, BPINP)
	for i in PINS:
		GPIO.setup(i, GPIO.OUT)
		if i != APINP or BPINP:
			GPIO.output(i, GPIO.LOW)
		else:
			GPIO.output(i, GPIO.HIGH)
