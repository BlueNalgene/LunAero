#!/bin/usr/python3 -B

class RasPiGPIO():
	'''Just a container for the pin definitions
	'''
	GPIO.setmode(GPIO.BCM)
	APINP = 17  #Pulse width pin for motor A (up and down)
	APIN1 = 27  #Motor control - high for up
	APIN2 = 22  #Motor control - high for down
	BPIN1 = 10  #Motor control - high for left
	BPIN2 = 9   #Motor control - high for right
	BPINP = 11  #Pulse width pin for motor B (right and left) 
