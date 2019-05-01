#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

"""
RT232->PCA9685->TB6612 Motor controller
Wesley T. Honeycutt - 2019
"""
# Native Imports
from math import floor
import time

class RPTControl():
	"""
	A class to control DC Motors through a RT232, PCA9685, TB6612 pipeline
	"""
	# Native Imports
	import busio
	# Third-Party imports
	# git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git
	# pip3 install Adafruit-GPIO
	import Adafruit_GPIO.FT232H as FT232H
	import Adafruit_PCA9685

	# Dictionary of magic numbers for the PCA9685 chip
	magic = {\
		"MODE1" : 0x00,\
		"MODE2" : 0x01,\
		"SUBADR1" : 0x02,\
		"SUBADR2" : 0x03,\
		"SUBADR3" : 0x04,\
		"PRESCALE" : 0xFE,\
		"LED0_ON_L" : 0x06,\
		"LED0_ON_H" : 0x07,\
		"LED0_OFF_L" : 0x08,\
		"LED0_OFF_H" : 0x09,\
		"ALL_LED_ON_L" : 0xFA,\
		"ALL_LED_ON_H" : 0xFB,\
		"ALL_LED_OFF_L" : 0xFC,\
		"ALL_LED_OFF_H" : 0xFD,\
		"RESTART" : 0x80,\
		"SLEEP" : 0x10,\
		"ALLCALL" : 0x01,\
		"INVRT" :0x10,\
		"OUTDRV" : 0x04\
		}

	clk_freq = 25000000.0
	resolution = 4096.0

	def __init__(self):
		"""
		Initialize class
		"""
		# Temporarily disable FTDI serial drivers.
		self.FT232H.use_FT232H()
		# Find the first FT232H device.
		ft232h = self.FT232H.FT232H()
		# Create an I2C device at address 0x70.
		self.i2c = self.FT232H.I2CDevice(ft232h, 0x70)
		# Initialise the PCA9685 using the default address (0x40).
		self.pwm = self.Adafruit_PCA9685.PCA9685(i2c=ft232h)
		return


	def set_pwm_freq_precisely(self, prescaler):
		"""
			Here directly set the (int) prescaler you want, for my PCA9685 board I get
			those values :
			60 = 108.7Hz, 70 = 93.46Hz, 80 = 81.97Hz, 90 = 72.46Hz, 95 = 68.43Hz,
			102 = 64.1Hz, 110 = 60.24Hz, 111 = 59.52Hz, 120 = 54.64Hz, 130 = 50.76Hz,
			140 = 46.73Hz, 150 = 43.48Hz, 160 = 41.15Hz, 170 = 38.46Hz
			THOSE VALUES ARE DIFFERENT FOR EACH BOARD, YOU HAVE TO MEASURE THEM YOURSELF
			see:
			electronics.stackexchange.com/questions/335825/setting-the-pca9685-pwm-module-prescaler
			TL:DR : PCA9685 was not meant for precision because it was made to drive LEDs not servos

			:param prescaler: - value which the prescaler should be adjusted to
		"""
		print("setting new prescaler value : {}".format(prescaler))
		oldmode = self.i2c.readU8(self.magic["MODE1"])
		newmode = (oldmode & 0x7F) | 0x10    # sleep
		self.i2c.write8(self.magic["MODE1"], newmode)  # go to sleep
		self.i2c.write8(self.magic["PRESCALE"], prescaler)
		self.i2c.write8(self.magic["MODE1"], oldmode)
		time.sleep(0.005)
		self.i2c.write8(self.magic["MODE1"], oldmode | 0x80)
		return

	def set_pwm_freq(self, freq_hz):
		"""
		Sets the frequency of the the PWM.

		:param freq_hz: - The clock frequency of the PWM desired, in Hertz
		"""
		float_prescaler = self.clk_freq/(self.resolution*freq_hz)
		round_prescaler = int(floor(float_prescaler + 0.5))
		oldmode = self.i2c.readU8(self.magic["MODE1"])
		newmode = (oldmode & 0x7F) | 0x10    # sleep
		self.i2c.write8(self.magic["MODE1"], newmode)  # go to sleep
		self.i2c.write8(self.magic["PRESCALE"], round_prescaler)
		self.i2c.write8(self.magic["MODE1"], oldmode)
		time.sleep(0.005)
		self.i2c.write8(self.magic["MODE1"], oldmode | 0x80)
		print("freq set to {} Hz".format(self.clk_freq/(round_prescaler*self.resolution)))
		return

	def set_pwm(self, channel, rise_edge, fall_edge):
		"""
		Sets a single PWM channel.
		To set full on use set_pwm(channel, 0, 4096)
		To set full off use set_pwm(channel, 4096, 0)

		:param channel: - PCA9685 channel from 0-15 to set.
		:param rise_edge: - The rising edge of the pmw clock.
		:param fall_edge: - The falling edge of the pwm clock.
		"""
		if not 0 <= channel <= 15:
			raise ValueError("input channel not within 0-15")
		if not 0 <= rise_edge <= 4096:
			raise ValueError("rising edge must be within precision range (0-4096)")
		if not 0 <= fall_edge <= 4096:
			raise ValueError("falling edge must be within precision range (0-4096)")
		print("setting pwm on channel {} to : ({}, {})".format(channel, rise_edge, fall_edge))
		self.i2c.write8(self.magic["LED0_ON_L"]+4*channel, rise_edge & 0xFF)
		self.i2c.write8(self.magic["LED0_ON_H"]+4*channel, rise_edge >> 8)
		self.i2c.write8(self.magic["LED0_OFF_L"]+4*channel, fall_edge & 0xFF)
		self.i2c.write8(self.magic["LED0_OFF_H"]+4*channel, fall_edge >> 8)

	def set_all_pwm(self, rise_edge, fall_edge):
		"""
		Sets all PWM channels.

		:param rise_edge: - The rising edge of the pmw clock.
		:param fall_edge: - The falling edge of the pwm clock.
		"""
		if not 0 <= rise_edge <= 4096:
			raise ValueError("rising edge must be within precision range (0-4096)")
		if not 0 <= fall_edge <= 4096:
			raise ValueError("falling edge must be within precision range (0-4096)")
		print("setting pwm all channel to to : ({}, {})".format(rise_edge, fall_edge))
		self.i2c.write8(self.magic["ALL_LED_ON_L"], rise_edge & 0xFF)
		self.i2c.write8(self.magic["ALL_LED_ON_H"], rise_edge >> 8)
		self.i2c.write8(self.magic["ALL_LED_OFF_L"], fall_edge & 0xFF)
		self.i2c.write8(self.magic["ALL_LED_OFF_H"], fall_edge >> 8)

	# DEPRECATED
	#def set_pulse_length(self, channel, pulse_length):
		#"""
			#used to drive servos, ledn_on is always 0 and ledn_off is pulse length
			#the pca9685 has a 4096 self.resolution so to get a 20% pwm you use a pulse_length
			#if 20% of 4096, the time of that pulse will depend of the current frequency
		#"""
		#self.set_pwm(channel, 0, pulse_length)

	def perc_to_pulse(self, perc):
		"""
		Converts a percent number (e.g. 20% aka 20) to the appropriate value for the bit self.resolution
		Ergo, 20% of 4096 is ~820.

		:param perc: - input percentage, float or int value.

		returns : - pulse - the output pulse value corrected for chip self.resolution
		"""
		if not 0 <= perc <= 100:
			raise ValueError("only percent values from 0-100 are accepted for input here")
		perc = perc / 100 #convert to decimal value
		pulse = perc * (self.resolution - 1)
		return int(pulse)




##   SAMPLE CODE   ##

#rpt = RPTControl()
#rpt.set_pwm_freq_precisely(70)
#rpt.set_pwm_freq(4000)


#try:
	#print('Moving servo on channel 0, press Ctrl-C to quit...')
	#while True:
		## Move servo on channel O between extremes.
		#rpt.pwm.set_pwm(1, 4096, 0)
		#rpt.pwm.set_pwm(2, 0, 4096)
		#rpt.pwm.set_pwm(0, 4096, 0)
		#rpt.pwm.set_pwm(3, 0, 4096)
		#rpt.pwm.set_pwm(4, 0, 0)
		#rpt.pwm.set_pwm(5, 0, 4096)
		#rpt.pwm.set_pwm(6, 0, 4096)
		#rpt.pwm.set_pwm(7, 0, 0)
		#rpt.pwm.set_pwm(8, 0, 4096)
		#rpt.pwm.set_pwm(9, 0, 4096)
		#rpt.pwm.set_pwm(10, 0, 0)
		#rpt.pwm.set_pwm(11, 0, 4096)
		#rpt.pwm.set_pwm(12, 0, 4096)
		#rpt.pwm.set_pwm(13, 0, 0)
		#rpt.pwm.set_pwm(14, 0, 4096)
		#rpt.pwm.set_pwm(15, 0, 4096)
		#time.sleep(1)
		#rpt.pwm.set_pwm(1, 0, 4096)
		#rpt.pwm.set_pwm(2, 4096, 0)
		#rpt.pwm.set_pwm(0, 4096, 0)
		#time.sleep(1)
#finally:
	#rpt.pwm.set_all_pwm(4096, 0)
	#time.sleep(1)
