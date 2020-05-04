"""
Motor control and recording for Lunaero

Motor A is up and down
Motor B is right and left
"""

# Standard imports
import io
import multiprocessing as mp
import os
import os.path
import subprocess
import sys
import threading
import time

# Non-standard imports
import cv2
import pygame

# Third Party imports
import numpy as np

# Special Mode Imports
from _datetime import datetime

# Local Imports

#position = (620, 20)
#os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])
pygame.display.init()
pygame.font.init()

# Get information for the current screen size.
SWID, SHEI = pygame.display.Info().current_w, pygame.display.Info().current_h
# Convert to the size of each quadrant of the screen
QWID = int(SWID/2)
QHEI = int(SHEI/2)

#white = (255, 255, 255)
RED = (255, 0, 0)
FONT = pygame.font.SysFont('monospace', 25)

SCREEN = pygame.display.set_mode((SWID, SHEI))

# Enable blind mode while tracking.
# True = don't display tracking window to save cpu cycles
# False = display visuals (default)
BLIND = False

# Select the device you are using.
# Raspberry Pi with Raspberry Pi Camera: 0
# Linux Computer with USB Camera: 1
# WiringPi Compatible Computer (Odroid N2) with USB Camera: 2
# WiringPi Compatible Computer (Odroid N2) with ActionCam: 3
# Raspberry Pi with ActionCam: 4
# TODO detect hardware
DEV = 0

#Enable logs with True, disable with False:
LOGS = False

#Asychronous Recording
ASYNC = True


class TextInput:
	"""
	Copyright 2017, Silas Gyger, silasgyger@gmail.com, All rights reserved.
	Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.
	This class lets the user input a piece of text, e.g. a name or a message.
	This class let's the user input a short, one-lines piece of text at a blinking cursor
	that can be moved using the arrow-keys. Delete, home and end work as well.
	"""
	def __init__(self, initial_string="", font_family="", font_size=35, antialias=True, \
		text_color=(255, 0, 0), cursor_color=(127, 0, 0), repeat_keys_initial_ms=400, \
			repeat_keys_interval_ms=35):
		"""
		:param initial_string: Initial text to be displayed
		:param font_family: name or list of names for font (see pygame.font.match_font
		for precise format)
		:param font_size:  Size of font in pixels
		:param antialias: Determines if antialias is applied to font (uses more processing power)
		:param text_color: Color of text (duh)
		:param cursor_color: Color of cursor
		:param repeat_keys_initial_ms: Time in ms before keys are repeated when held
		:param repeat_keys_interval_ms: Interval between key press repetition when helpd
		"""
		# Text related vars:
		self.antialias = antialias
		self.text_color = text_color
		self.font_size = font_size
		self.input_string = initial_string  # Inputted text
		# Fonts
		if not os.path.isfile(font_family):
			font_family = pygame.font.match_font(font_family)
		self.font_object = pygame.font.Font(font_family, font_size)
		# Text-surface will be created during the first update call:
		self.surface = pygame.Surface((1, 1))
		self.surface.set_alpha(0)
		# Vars to make keydowns repeat after user pressed a key for some time:
		self.keyrepeat_counters = {}  # {event.key: (counter_int, event.unicode)} (look for "***")
		self.keyrepeat_intial_interval_ms = repeat_keys_initial_ms
		self.keyrepeat_interval_ms = repeat_keys_interval_ms
		# Things cursor:
		self.cursor_surface = pygame.Surface((int(self.font_size/20+1), self.font_size))
		self.cursor_surface.fill(cursor_color)
		self.cursor_position = len(initial_string)  # Inside text
		self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
		self.cursor_switch_ms = 500  # /|\
		self.cursor_ms_counter = 0
		# Init clock
		self.clock = pygame.time.Clock()
	def update(self, events):
		"""Update the values in the box
		"""
		for event in events:
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.KEYDOWN:
				self.cursor_visible = True  # So the user sees where he writes
				# If none exist, create counter for that key:
				if event.key not in self.keyrepeat_counters:
					self.keyrepeat_counters[event.key] = [0, event.unicode]
				if event.key == pygame.K_BACKSPACE:
					self.input_string = (self.input_string[:max(self.cursor_position - 1, 0)] + \
						self.input_string[self.cursor_position:])
					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)
				elif event.key == pygame.K_DELETE:
					self.input_string = (self.input_string[:self.cursor_position] + \
						self.input_string[self.cursor_position + 1:])
				elif event.key == pygame.K_RETURN:
					print(str(self.input_string))
					return True
				elif event.key == pygame.K_RIGHT:
					# Add one to cursor_pos, but do not exceed len(input_string)
					self.cursor_position = min(self.cursor_position + 1, len(self.input_string))
				elif event.key == pygame.K_LEFT:
					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)
				elif event.key == pygame.K_END:
					self.cursor_position = len(self.input_string)
				elif event.key == pygame.K_HOME:
					self.cursor_position = 0
				else:
					# If no special key is pressed, add unicode of key to input_string
					self.input_string = (self.input_string[:self.cursor_position] + \
						event.unicode + self.input_string[self.cursor_position:])
					self.cursor_position += len(event.unicode)  # Some are empty, e.g. K_UP
			elif event.type == pygame.KEYUP:
				# *** Because KEYUP doesn't include event.unicode,
				#this dict is stored in such a weird way
				if event.key in self.keyrepeat_counters:
					del self.keyrepeat_counters[event.key]
		# Update key counters:
		for key in self.keyrepeat_counters:
			self.keyrepeat_counters[key][0] += self.clock.get_time()  # Update clock
			# Generate new key events if enough time has passed:
			if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
				self.keyrepeat_counters[key][0] = (self.keyrepeat_intial_interval_ms - \
					self.keyrepeat_interval_ms)
				event_key, event_unicode = key, self.keyrepeat_counters[key][1]
				pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=event_key,\
					unicode=event_unicode))
		# Re-render text surface:
		self.surface = self.font_object.render(self.input_string, self.antialias, self.text_color)
		# Update self.cursor_visible
		self.cursor_ms_counter += self.clock.get_time()
		if self.cursor_ms_counter >= self.cursor_switch_ms:
			self.cursor_ms_counter %= self.cursor_switch_ms
			self.cursor_visible = not self.cursor_visible
		if self.cursor_visible:
			cursor_y_pos = self.font_object.size(self.input_string[:self.cursor_position])[0]
			# Without this, the cursor is invisible when self.cursor_position > 0:
			if self.cursor_position > 0:
				cursor_y_pos -= self.cursor_surface.get_width()
			self.surface.blit(self.cursor_surface, (cursor_y_pos, 0))
		self.clock.tick()
		return False
	def get_surface(self):
		"""
		Called to get the surface
		"""
		return self.surface
	def get_text(self):
		"""
		Called to get the text string
		"""
		return self.input_string
	def get_cursor_position(self):
		"""
		Called to get the cursor position
		"""
		return self.cursor_position
	def set_text_color(self, color):
		"""
		Called to set the color of the text
		"""
		self.text_color = color
	def set_cursor_color(self, color):
		"""
		Called to set the color of the mouse cursor
		"""
		self.cursor_surface.fill(color)
	def clear_text(self):
		"""
		Called to clear the text string.
		"""
		self.input_string = ""
		self.cursor_position = 0

class TimeLoop():
	"""
	This class contains screens which ask the user to verify the time listed on the raspberry pi.
	The intended use is to provide for instances when the pi is not able to auto sync the clock
	with an internet connection, yet not use an RTC.
	"""
	tix = TextInput()
	def __init__(self):
		"""
		:param startup: Toggle switch for while loop
		:param timetuple: Empty tuple to hold time values
		:param mrgn: Margin around text to act as padding
		:param ftsz: Font size in points
		"""
		self.startup = True
		self.timetuple = ()
		self.mrgn = 10
		self.ftsz = 25

	def firstcheck(self):
		"""
		Ask the user to confirm that the time is correct
		"""
		timetuple = ()
		while self.startup:
			SCREEN.fill((0, 0, 0))
			lctn = self.mrgn + self.ftsz
			hpos = QWID - 22*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render('-----------------CHECK CLOCK-----------------', True, RED),\
				(hpos, lctn))
			lctn = lctn + self.ftsz + self.mrgn
			SCREEN.blit(FONT.render('        Does this time seem correct?         ', True, RED),\
				(hpos, lctn))
			lctn = lctn + self.ftsz + self.mrgn
			hpos = QWID - round(len(self.thetime())/2)*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render(str(self.thetime()), True, RED), (hpos, lctn))
			lctn = lctn + self.ftsz + self.mrgn
			hpos = QWID - 22*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render('          Press: [y]es or [n]o....           ', True, RED),\
				(hpos, lctn))
			pygame.display.update()
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_y:
						return True
					if event.key == pygame.K_n:
						if LOGS:
							print("changing time")
						pygame.time.wait(100)
						i = 0
						while i < 6:
							timetuple += (int(self.timeinput(i)),)
							i += 1
						# Add milliseconds
						timetuple += (0,)
						if LOGS:
							print(timetuple)
						while not self.tzpick():
							pass
						self.startup = not self.startup
		return timetuple

	def timeinput(self, ith):
		"""
		Pygame.  Constructs a tuple of date values to use when setting the date and time
		"""
		while True:
			SCREEN.fill((0, 0, 0))
			lctn = self.mrgn + self.ftsz
			hpos = QWID - 22*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render('-----------------CHECK CLOCK-----------------', True, RED),\
				(hpos, lctn))
			lctn = lctn + self.ftsz + self.mrgn
			hpos = QWID - 22*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render('Enter the date/time as accurately as possible', True, RED),\
				(hpos, lctn))
			lctn = lctn + self.ftsz + self.mrgn
			hpos = QWID - 11*(self.ftsz-self.mrgn)
			if ith == 0:
				SCREEN.blit(FONT.render('Year (last two-digits)', True, RED), (hpos, lctn))
			elif ith == 1:
				SCREEN.blit(FONT.render('Month (two-digits)', True, RED), (hpos, lctn))
			elif ith == 2:
				SCREEN.blit(FONT.render('Day (two-digits)', True, RED), (hpos, lctn))
			elif ith == 3:
				SCREEN.blit(FONT.render('Hour (two-digits)', True, RED), (hpos, lctn))
			elif ith == 4:
				SCREEN.blit(FONT.render('Minute (two-digits)', True, RED), (hpos, lctn))
			elif ith == 5:
				SCREEN.blit(FONT.render('Second (two-digits)', True, RED), (hpos, lctn))
			hpos = QWID + 11*(self.ftsz-self.mrgn)
			events = pygame.event.get()
			SCREEN.blit(self.tix.get_surface(), (hpos, lctn))
			if self.tix.update(events):
				outputstring = self.tix.get_text()
				if len(outputstring) == 2 and outputstring.isdigit():
					self.tix.clear_text()
					if ith == 0:
						outputstring = 2000 + int(outputstring)
					return outputstring
				else:
					self.badinput(lctn)
			pygame.display.update()

	def badinput(self, blah):
		"""
		Pygame.  Complains to the user if they input an invalid string for the date values and
		prompts them to try again.
		"""
		trigger = True
		while trigger:
			lctn = blah + self.ftsz + self.mrgn
			hpos = QWID - 22*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render('xxxxxxxxxxxxxx TWO DIGITS ONLY xxxxxxxxxxxxxx', True, RED),\
				(hpos, lctn))
			lctn = lctn + self.ftsz + self.mrgn
			SCREEN.blit(FONT.render(' Press [Return] to re-enter that value. . .  ', True, RED),\
				(hpos, lctn))
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						self.tix.clear_text()
						pygame.time.wait(300)
						trigger = False
			pygame.display.update()
		pygame.display.update()
		return

	def tzpick(self):
		"""
		Pygame.  Multiple choice selection for timezone
		Sets the timezone when finished.
		"""
		trigger = True
		SCREEN.fill((0, 0, 0))
		lctn = self.mrgn + self.ftsz
		hpos = QWID - 22*(self.ftsz-self.mrgn)
		SCREEN.blit(FONT.render('Which timezone are you in right now?         ', \
			True, RED), (hpos, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		hpos = QWID - 11*(self.ftsz-self.mrgn)
		SCREEN.blit(FONT.render('[a] - UTC', True, RED), (hpos, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('[b] - Pacific', True, RED), (hpos, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('[c] - Mountain', True, RED), (hpos, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('[d] - Central', True, RED), (hpos, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('[e] - Eastern', True, RED), (hpos, lctn))
		while trigger:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_a:
						os.environ['TZ'] = 'America/Los_Angeles'
						trigger = False
					elif event.key == pygame.K_b:
						os.environ['TZ'] = 'America/Denver'
						trigger = False
					elif event.key == pygame.K_c:
						os.environ['TZ'] = 'Europe/London'
						trigger = False
					elif event.key == pygame.K_d:
						os.environ['TZ'] = 'America/Chicago'
						trigger = False
					elif event.key == pygame.K_e:
						os.environ['TZ'] = 'America/New_York'
						trigger = False
			pygame.display.update()
		time.tzset()
		return True

	def thetime(self):
		"""
		This function simply grabs the current time with the time zone and returns it.

		:returns: - outval - time formatted as a string with the timezone included
		"""
		outval = time.time()
		outval = datetime.fromtimestamp(outval)
		outval = outval.strftime('%Y-%m-%d %H:%M:%S')
		outval = str(outval) + "  " + str(time.localtime().tm_zone)
		return outval

	def timeloop_running(self):
		"""
		Executes a time loop function.  Use as a while loop threshold until it returns false.

		:returns: - False - when finished
		"""
		timeval = self.firstcheck()
		while not timeval:
			pass
		if isinstance(timeval, tuple):
			self._linux_setdate(timeval)
			pygame.time.wait(500)
		return False

	def _linux_setdate(self, time_tuple):
		"""
		This function sets the time of the system based on a tuple of values.
		:param time_tuple: This is the tuple which represents the target time setting.
		Subvalues are:
			Year (needs to be 4 digits)
			Month (the rest are 2 digits)
			Day
			Hour
			Minute
			Second
			Millisecond
		"""
		import shlex
		time_string = datetime(*time_tuple).isoformat()
		#subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
		subprocess.call(shlex.split("sudo date -s '%s'" % time_string))
		#subprocess.call(shlex.split("sudo hwclock -w"))
		return


class FFmpegVideoCapture():
	"""
	Adapted from:
	Reading video from FFMPEG using subprocess - aka when OpenCV VideoCapture fails
	By:
	Emanuele Ruffaldi 2016
	"""
	def __init__(self, source="rtsp://127.0.0.1:8554", width=640, height=360):
		"""
		Initialize the FFMPEG hack stream
		:param source: The source of the udp stream, defaults to ActionCam default
		:param width: The width of the image stream, defaults to 640
		:param height: The height of the image stream, defaults to 360
		"""
		# Find local parameters of the go environment
		self.gopath = str(self.goget())
		self.gopath = self.gopath + "/bin/actioncam"
		# Run FFMPEG to capture the stream
		self.ffmpeg = subprocess.Popen(["ffmpeg", "-i", source, "-f", "rawvideo", "-pix_fmt",\
			"yuv420p", "-"], stdout=subprocess.PIPE)
		# Local Size Variables
		self.width = width
		self.height = height
		self.halfh = int(self.height/2)
		self.halfw = int(self.width/2)
		self.fsize = int(width*height*6/4)
		# Read the output of the stream to confirm we are getting whatwe expect
		self.output = self.ffmpeg.stdout
	def read(self):
		"""
		This function reads the image from the buffer stream.
		:returns: - ret - Confirmation that this captured an image
		- result - The image that was pulled (w=640, h=360, bgr)
		"""
		if self.ffmpeg.poll():
			return False, None
		out = self.output.read(self.fsize)
		if out == "":
			return False, None
		# Y fullsize
		# U w/2 h/2
		# V w/2 h/2
		area = int(self.width * self.height)
		# Get the y, u, and v signals from the ffmpeg stream
		yyy = np.frombuffer(out[0:area], dtype=np.uint8).reshape((self.height, self.width))
		uuu = np.frombuffer(out[area:area + int(area/4)],\
			dtype=np.uint8).reshape((self.halfh, self.halfw))
		vvv = np.frombuffer(out[area+int(area/4):], \
			dtype=np.uint8).reshape((self.halfh, self.halfw))
		# Resize the shrunken u and v streams to meet the y size
		uuu = cv2.resize(uuu, (self.width, self.height))
		vvv = cv2.resize(vvv, (self.width, self.height))
		# Merge the yuv and convert to the more useful BGR
		result = cv2.merge((yyy, uuu, vvv))
		result = cv2.cvtColor(result, cv2.COLOR_YUV2BGR)
		return True, result
	def goget(self):
		"""
		This function returns the golang environmental path for the system
		"""
		return subprocess.check_output(["go", "env", "GOPATH"]).decode().strip('\n')
	def start_server(self):
		"""
		This function starts the RTSP server.  It must be run using a non-blocking method.
		"""
		proc = subprocess.Popen([self.gopath, "rtsp", "192.168.100.1"],\
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#out, err = proc.communicate()
		return proc
	def killcamera(self):
		"""
		Kills the camera stream
		"""
		#TODO
		return

class MotorFunctions():
	"""
	Functions which are unique to the motor control system used in LunAero
	"""
	if DEV in (0, 4):
		import RPi.GPIO as GPIO
	elif DEV == 1:
		import Adafruit_GPIO as GPIO
		import Adafruit_GPIO.FT232H as FT232H
		# Local Imports
		from Moontracker_Classes import rpt_control
		rpt = rpt_control.RPTControl()
	elif DEV in (2, 3):
		import wiringpi as wpi
	else:
		raise IOError("Invalid Hardware Selected")
	def __init__(self):
		"""Initialize the GPIO pins by associating the values of the pins we are using to variable.
		Initalize two pins with software controlled PWM with requisite duty cycles and freq.
		Start these PWM when they are ready.
		Assign values to the motion and ratio thresholds
'		"""
		# Defines the pins being used for the GPIO pins.
		if LOGS:
			print("Defining GPIO pins")
		if DEV in (0, 4):
			self.GPIO.setmode(self.GPIO.BCM)
			self.apinp = 17  #Pulse width pin for motor A (up and down)
			self.apin1 = 27  #Motor control - high for up
			self.apin2 = 22  #Motor control - high for down
			self.bpin1 = 10  #Motor control - high for left
			self.bpin2 = 9   #Motor control - high for right
			self.bpinp = 11  #Pulse width pin for motor B (right and left)
			# Setup GPIO and start them with 'off' values
			pins = (self.apin1, self.apin2, self.apinp, self.bpin1, self.bpin2, self.bpinp)
			for i in pins:
				self.GPIO.setup(i, self.GPIO.OUT)
				if i != self.apinp or self.bpinp:
					self.GPIO.output(i, self.GPIO.LOW)
				else:
					self.GPIO.output(i, self.GPIO.HIGH)
		elif DEV == 1:
			self.rpt.set_pwm_freq_precisely(70)
			self.rpt.set_pwm_freq(4000)
			self.apinp = 0   #Pulse width pin for motor A (up and down)
			self.apin1 = 2   #Motor control - high for up
			self.apin2 = 1   #Motor control - high for down
			self.bpin1 = 3   #Motor control - high for left
			self.bpin2 = 4   #Motor control - high for right
			self.bpinp = 5   #Pulse width pin for motor B (right and left)
		elif DEV in (2, 3):
			self.wpi.wiringPiSetup()
			self.apinp = 0   #Pulse width pin for motor A (up and down)
			self.apin1 = 2   #Motor control - high for up
			self.apin2 = 3   #Motor control - high for down
			self.bpin1 = 12  #Motor control - high for left
			self.bpin2 = 13  #Motor control - high for right
			self.bpinp = 14  #Pulse width pin for motor B (right and left)
			# Setup GPIO and start them with 'off' values
			pins = (self.apin1, self.apin2, self.apinp, self.bpin1, self.bpin2, self.bpinp)
			for i in pins:
				self.wpi.pinMode(i, 1)
				if i not in (self.apinp, self.bpinp):
					self.wpi.digitalWrite(i, 0)
				else:
					self.wpi.softPwmCreate(i, 0, 100)
		else:
			raise IOError("Invalid Hardware Selected")
		freq = 10000
		self.dca = 0                             # Set duty cycle variable to zero at first
		self.dcb = 0
		if DEV in (0, 4):
			self.pwma = self.pwm(self.apinp, freq)   # Initialize PWM on pwmPins
			self.pwmb = self.pwm(self.bpinp, freq)
			self.pwma.start(self.dca)                # Start pulse width at 0 (pin held low)
			self.pwmb.start(self.dcb)                # Start pulse width at 0 (pin held low)
		elif DEV in (2, 3):
			self.wpi.softPwmWrite(self.apinp, self.dca)
			self.wpi.softPwmWrite(self.bpinp, self.dcb)
		self.acount = 0
		self.bcount = 0
		self.olddir = 0                          # Stores old movement direction; 1 left, 2 right
		self.aspect = QWID/QHEI
		# the moon must be displaced by this amount for movement to occur.
		self.lostratio = 0.001                   # a percentage of frame height
		self.vtstop = 0.055 * QHEI   #offset to stop vertical movement (must be < Start)
		self.htstop = 0.05 * QWID     #image offset to stop horizontal movement (must be < Start)
		# Set a counter to ensure we don't move in the same direction too long
		self.move_count_x = 0
		self.move_count_y = 0
		self.prev_dir_x = 0
		self.prev_dir_y = 0
		self.move_count_thresh = 200
		return
	def pinhigh(self, channel):
		"""
		Pulls a pin high based on the method for the RPi or computer controls

		:param channel: - Channel/pin to set high.
		"""
		if DEV in (0, 4):
			self.GPIO.output(channel, self.GPIO.HIGH)
		elif DEV == 1:
			self.rpt.set_pwm(channel, 4096, 0)
		elif DEV in (2, 3):
			self.wpi.digitalWrite(channel, 1)
		else:
			raise IOError("Invalid Hardware Selected")
		return
	def pinlow(self, channel):
		"""
		Pulls a pin low based on the method for the RPi or computer controls

		:param channel: - Channel/pin to set low.
		"""
		if DEV in (0, 4):
			self.GPIO.output(channel, self.GPIO.LOW)
		elif DEV == 1:
			self.rpt.set_pwm(channel, 0, 4096)
		elif DEV in (2, 3):
			self.wpi.digitalWrite(channel, 0)
		else:
			raise IOError("Invalid Hardware Selected")
		return
	def setduty(self, motor):
		"""
		Sets a duty cycle of a pin based on the method for the RPi or computer controls

		:param motor: - byte letter (python format string) used to denote which motor we want
		to control.  Either 'A' or 'B'.
		"""
		if DEV in (0, 4):
			if motor == 'A':
				self.pwma.ChangeDutyCycle(self.dca)
			elif motor == 'B':
				self.pwmb.ChangeDutyCycle(self.dcb)
			else:
				raise RuntimeError("asked to set duty cycle for non-existant motor")
		elif DEV == 1:
			if motor == 'A':
				self.rpt.set_pwm(self.apinp, 1, self.rpt.perc_to_pulse(self.dca))
			elif motor == 'B':
				self.rpt.set_pwm(self.bpinp, 1, self.rpt.perc_to_pulse(self.dcb))
			else:
				raise RuntimeError("asked to set duty cycle for non-existant motor")
		elif DEV in (2, 3):
			if motor == 'A':
				self.wpi.softPwmWrite(self.apinp, self.dca)
			elif motor == 'B':
				self.wpi.softPwmWrite(self.bpinp, self.dcb)
			else:
				raise RuntimeError("asked to set duty cycle for non-existant motor")
		else:
			raise IOError("Invalid Hardware Selected")
	def loose_wheel(self):
		"""
		Gives some extra umph when changing direction for the looser horizontal gear
		"""
		if LOGS:
			print("Left Right power move")
		self.dcb = 100
		self.setduty('B')
		# Sets movement in opposite direction, remember that this will be backwards!
		if self.olddir == 1:
			self.motright()
		elif self.olddir == 2:
			self.motleft()
		pygame.time.wait(3000)
		self.dcb = 25
		self.setduty('B')
	def sustained_movement(self, direct):
		"""
		Check to see if we are still moving in the same direciton
		If so, add to a counter
		If we surpass a threshold, crash.
		
		:param direct: - the direction we are currently moving (0 null, 1 up, 2 down, 3 left, 4 right, 12 neither up nor down, 34 neither left nor right))
		"""
		if direct == (1, 2):
			if self.prev_dir_y == direct:
				self.move_count_y += 1
			else:
				self.move_count_y = 0
			if self.move_count_y > self.move_count_thresh:
				raise RuntimeError("moving in the same direction too long (y)")
			self.prev_dir_y = direct
		elif direct == (3, 4):
			if self.prev_dir_x == direct:
				self.move_count_x += 1
			else:
				self.move_count_x = 0
			if self.move_count_x > self.move_count_thresh:
				raise RuntimeError("moving in the same direction too long (x)")
			self.prev_dir_x = direct
		elif direct == 12:
			self.prev_dir_y = 0
			self.move_count_y = 0
		elif direct == 34:
			self.prev_dir_x = 0
			self.move_count_x = 0
		return
	def check_move(self, diffx, diffy, ratio):
		"""
		Check the values for the difference between x and y of the observed image to the
		perfect center of the screen and move the camera to center the image
		"""
		if ratio < self.lostratio:
			return 2
		else:
			if abs(diffx) < abs((diffy*self.aspect)):
				if abs(diffy) > self.vtstop:
					if diffy > 0:
						self.motup()
						self.sustained_movement(1)
					else:
						self.motdown()
						self.sustained_movement(2)
					self.speedup("Y")
					return 0
			else:
				if abs(diffx) > self.htstop:
					if diffx > 0:
						if self.olddir == 2:
							self.loose_wheel()
						self.motleft()
						self.sustained_movement(3)
					else:
						if self.olddir == 1:
							self.loose_wheel()
						self.motright()
						self.sustained_movement(4)
					self.speedup("X")
					return 0
			if (abs(diffx) < self.htstop and self.dcb > 0):
				self.motstop("X")
				self.sustained_movement(34)
				return 0
			if (abs(diffy) < self.vtstop and self.dca > 0):
				self.motstop("Y")
				self.sustained_movement(12)
				return 0
		if (abs(diffx) < self.htstop and abs(diffy) < self.vtstop):
			self.motstop("B")
			self.sustained_movement(12)
			self.sustained_movement(34)
			return 1
	def motstop(self, direct):
		"""
		Stops the motors in an intelligent way
		:param direct: Which directional motor are you stopping? X, Y, or Both?
		"""
		if LOGS:
			print("stopping", direct)
		if direct == "B":
			while self.dca > 0 or self.dcb > 0:
				if self.dca > 10:
					self.dca = 10     #quickly stop motor going full speed
				else:
					self.dca = self.dca - 1   #slowly stop motor going slow (tracking moon)
				if self.dcb > 10:
					self.dcb = 10
				else:
					self.dcb = self.dcb - 1
				self.setduty('A')
				self.setduty('B')
				time.sleep(.005)
			self.pinlow(self.apin1)
			self.pinlow(self.apin2)
			self.pinlow(self.bpin1)
			self.pinlow(self.bpin2)
		elif direct == "Y":
			while self.dca > 0:
				self.dca = self.dca - 1
				self.setduty('A')
				time.sleep(.01)
			self.pinlow(self.apin1)
			self.pinlow(self.apin2)
		elif direct == "X":
			while self.dcb > 0:
				self.dcb = self.dcb - 1
				self.setduty('B')
				time.sleep(.01)
			self.pinlow(self.bpin1)
			self.pinlow(self.bpin2)
		return
	def motdown(self):
		"""
		Move motors to point scope DOWN
		"""
		if LOGS:
			print("moving down")
		self.pinhigh(self.apin1)
		self.pinlow(self.apin2)
		return
	def motup(self):
		"""
		Move motors to point scope UP
		"""
		if LOGS:
			print("moving up")
		self.pinlow(self.apin1)
		self.pinhigh(self.apin2)
		return
	def motright(self):
		"""
		Move motors to point scope RIGHT
		"""
		if LOGS:
			print("moving right")
		self.olddir = 2
		self.pinhigh(self.bpin1)
		self.pinlow(self.bpin2)
		return
	def motleft(self):
		"""
		Move motors to point scope LEFT
		"""
		if LOGS:
			print("moving left")
		self.olddir = 1
		self.pinlow(self.bpin1)
		self.pinhigh(self.bpin2)
		return
	def speedup(self, direct):
		"""
		Increase the motor speed by altering the duty cycle of the motor
		:param direct: Which motor? X or Y?
		The acount/bcount switch increases speed at a slower rate for already high speeds,
		this prevents zooming about too much.
		"""
		if direct == "Y":
			if self.dca < 10:
				self.dca = 10
			elif self.dca < 25:
				self.dca += 1
			elif self.dca < 40:
				if self.acount > 2:
					self.dca += 1
					self.acount = 0
				else:
					self.acount += 1
			self.setduty('A')
			if LOGS:
				print("speedup ", direct, self.dca)
		elif direct == "X":
			if self.dcb < 10:
				self.dcb = 10
			elif self.dcb < 25:
				self.dcb += 1
			elif self.dcb < 40:
				if self.bcount > 2:
					self.dcb += 1
					self.bcount = 0
				else:
					self.bcount += 1
			self.setduty('B')
			print("speedup", direct, self.dcb)
		return
	def setdc(self, ina, inb):
		"""
		Used to set the dutycycle from outside the class

		:param ina: the input value for the duty cycle setting for motor A
		:param inb: the input value for the duty cycle setting for motor B
		"""
		self.dca = ina
		self.dcb = inb
		return
	def wait_timer(self):
		"""This function checks the current move speed of the motor and outputs a value for
		pygame.wait which has an inverse relationship to the speed.
		returns - val - ms delay period for pygame.wait function
		"""
		from math import exp
		speed = max(self.dca, self.dcb)
		val = int(2560*exp(-.1386*speed))
		return val
	def cleanup(self):
		""" Required to be called at end of program
		"""
		if DEV in (0, 4):
			self.GPIO.cleanup()
		elif DEV == 1:
			self.rpt.pwm.set_all_pwm(4096, 0)
		elif DEV in (2, 3):
			self.wpi.softPwmWrite(self.apinp, 0)
			self.wpi.softPwmWrite(self.bpinp, 0)
			for i in (self.apin1, self.apin2, self.bpin1, self.bpin2):
				self.pinlow(i)
		else:
			raise IOError("Invalid Hardware Selected")
		return
	#def demo_on(self):
		##TEST Remove this portion if you are done with it.
		#self.pinhigh(13)
		#self.pinlow(14)
		#self.rpt.set_pwm(15, 1, self.rpt.perc_to_pulse(25))
		#return
	#def demo_off(self):
		##TEST Remove this portion if you are done with it.
		#self.pinlow(13)
		#self.pinlow(14)
		#self.pinlow(15)
		#return


class VideoCaptureAsync:
	"""
	from http://blog.blitzblit.com/2017/12/24/asynchronous-video-capture-in-python-with-opencv/
	"""
	def __init__(self, src=0, width=1920, height=1080):
		"""
		:param src: - Source of stream for cv2.VideoCapture
		:param width: - width of stream
		:param height: - height of stream
		"""
		self.src = src
		self.cap = cv2.VideoCapture(self.src)
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
		self.grabbed, self.frame = self.cap.read()
		self.started = False
		self.read_lock = threading.Lock()

	def set(self, var1, var2):
		"""
		Sets the variables you input
		"""
		self.cap.set(var1, var2)

	def start(self):
		"""
		Start the threaded stream
		"""
		if self.started:
			print('[!] Asynchroneous video capturing has already been started.')
			return None
		self.started = True
		self.thread = threading.Thread(target=self.update, args=())
		self.thread.start()
		return self

	def update(self):
		"""
		Update the threaded stream
		"""
		while self.started:
			grabbed, frame = self.cap.read()
			with self.read_lock:
				self.grabbed = grabbed
				self.frame = frame

	def read(self):
		"""
		Read from the stream
		"""
		with self.read_lock:
			frame = self.frame.copy()
			grabbed = self.grabbed
		return grabbed, frame

	def stop(self):
		"""
		Stop the stream
		"""
		self.started = False
		self.thread.join()

	def __exit__(self, exec_type, exc_value, traceback):
		"""
		Graceful Exit
		"""
		self.cap.release()







class CameraFunctions():
	"""This class provides the camera functions of for LunAero.
	Requires PILLOW and the default picamera package.
	"""
	import glob
	if DEV == 0:
		import picamera
	elif DEV in (1, 2, 3, 4):
		pass
	else:
		raise IOError("Invalid Hardware Selected")
	from PIL import Image
	clist = [ \
		"brightness", \
		"contrast", \
		"saturation", \
		"hue", \
		"white_balance_temperature_auto", \
		"gamma", \
		"gain", \
		"power_line_frequency", \
		"white_balance_temperature", \
		"sharpness", \
		"backlight_compensation", \
		"exposure_auto", \
		"exposure_absolute", \
		"exposure_auto_priority" \
		]
	def __init__(self, ffh):
		"""
		Initalize the camera
		Get some important values about the image from the camera
		Create some placeholders for the byte stream
		Get screen information locally and create a byte array to hold some more data.
		"""
		self.ffh = ffh
		self.start = time.time()
		self.surf = ''
		self.vwr = None
		self.iso = 200
		self.imgthresh = 125
		self.oldx = None
		self.oldy = None
		self.frame = None
		self.framecnt = 0
		# Byte streaming holder
		#self.stream = io.BytesIO()
		# Image Processing Values
		#self.imgthresh = 125
		self.lostcount = 0 #Always initialize at 0
		# Camera information
		if DEV in (0, 4):
			self.folder = "/media/pi/MOON1/" + str(int(self.start))
		elif DEV == 1:
			self.folder = "/scratch/whoneyc/" + str(int(self.start))
		elif DEV in (2, 3):
			self.folder = "/home/odroid/Documents/Vids_LunAero/" + str(int(self.start))
		else:
			raise IOError("Invalid Hardware Selected")
		os.makedirs(self.folder)
		print(self.start)
		print("Preparing outfile")
		if DEV == 0:
			self.camera = self.picamera.PiCamera()
			self.camera.led = False
			self.camera.video_stabilization = True
			self.camera.resolution = (1920, 1080)
			self.camera.color_effects = (128, 128) # turn camera to black and white
		elif DEV in (1, 2):
			list_of_cameras = self.glob.glob("/dev/video*")
			for i in list_of_cameras:
				try:
					ppp = str(subprocess.check_output(["v4l2-ctl", "-d", i, "--info"]))
					if "USB Camera" in ppp:
						self.camstring = i
						if "2.0" in ppp:
							self.camtoggle = 2
						elif "3.0" in ppp:
							self.camtoggle = 3
				except subprocess.CalledProcessError:
					pass
			if self.camstring == '':
				raise RuntimeError("No USB camera matching description found")
			if self.camtoggle == 2:
				subprocess.check_call(["v4l2-ctl", "-d", self.camstring, "-v",\
					"width=1024,height=768,pixelformat=MJPG -p 30"])
			elif self.camtoggle == 3:
				subprocess.check_call(["v4l2-ctl", "-d", self.camstring, "-v",\
					"width=1920,height=1080,pixelformat=MJPG -p 60"])
			# Set powerline to 60Hz
			self.set_v4l2_cam(7, 2)
			# Set manual exposure mode
			self.set_v4l2_cam(11, 1)
			print(subprocess.check_call(["v4l2-ctl", "-d", self.camstring, "-V"]))
			if ASYNC:
				self.camera = VideoCaptureAsync(int(self.camstring.strip("/dev/video")))
			else:
				self.camera = cv2.VideoCapture(int(self.camstring.strip("/dev/video")))
			self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
			if self.camtoggle == 3:
				self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
				self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
			elif self.camtoggle == 2:
				self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
				self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
			self.camera.set(cv2.CAP_PROP_FPS, 30)
			self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
		elif DEV in (3, 4):
			# We don't need to do anything fancy for the ActionCam
			pass
		else:
			raise IOError("Invalid Hardware Selected")
		#self.iso = 200
		# Image surface holder for pygame
		self.cenx, self.ceny = QWID/4, QHEI/4   #center of image
		self.prerat = float(QWID)*float(QHEI)
		self.rgb = bytearray(800 * 600 * 4)
		self.rln = len(self.rgb)
		# Fresh Image
		self.getimg()
		self.surfit()
		return
	def set_v4l2_cam(self, arg, val):
		"""Syntax for the linux expression to change a setting using v4l2-ctl
		:param arg: - The setting we are changing.  Must be an int which refers to the correct
		value in the clist.
		:param val: - The value we want to change arg to
		"""
		subprocess.check_call([\
			"v4l2-ctl",\
			"-d", self.camstring,\
			"-c", self.clist[arg] + "=" + str(val)])
		return
	def get_v4l2_cam(self, arg):
		"""Syntax for the linux expression to fetch a setting using v4l2-ctl
		:param arg: - The setting we are fetching.  Must be an int which refers to the correct
		value in the clist.
		"""
		ret = subprocess.check_output([\
			"v4l2-ctl",\
			"-d", self.camstring,\
			"-C", self.clist[arg]])
		return ret
	def startrecord(self):
		"""
		Tell the picamera to start recording whatever we are looking at to file.  This outputs raw
		video with a non-standard framerate.  The framerate must be calculated from the exposure
		setting of the camera.
		"""
		self.start = time.time()
		self.get_exposure_folder()
		if DEV == 0:
			outfile = str(int(self.start)) + 'outA.h264'
			outfile = os.path.join(self.folder, outfile)
			print(str(outfile))
			self.camera.start_recording(outfile)
		elif DEV in (1, 2):
			outfile = str(int(self.start)) + 'outA.avi'
			outfile = os.path.join(self.folder, outfile)
			print(str(outfile))
			fourcc = cv2.VideoWriter_fourcc(*'MJPG')
			if self.camtoggle == 2:
				self.vwr = cv2.VideoWriter(outfile, fourcc, 25, (1024, 768))
			elif self.camtoggle == 3:
				self.vwr = cv2.VideoWriter(outfile, fourcc, 25, (1920, 1080))
			if ASYNC:
				self.camera.start()
			#self.vwr = cv2.VideoWriter(outfile, 0x21, 30, (1024, 768))
		elif DEV in (3, 4):
			# We don't record video in this case
			pass
		time.sleep(1)
		return
	def getimg(self, rec=False):
		"""
		Capture an image and see how close it is to center
		"""
		if LOGS:
			start = time.time()
		if DEV == 0:
			self.stream = io.BytesIO()
			self.camera.capture(self.stream, use_video_port=True, resize=(800, 600),\
				format='rgba')
			self.stream.seek(0)
			self.stream.readinto(self.rgb)
			self.stream.close()
		elif DEV in (1, 2):
			if ASYNC:
				_, self.frame = self.camera.read()
				if rec:
					self.vwr.write(self.frame)
				else:
					self.camera.update()
			else:
				if self.camera.isOpened(): # try to get the first frame
					_, self.frame = self.camera.read()
					if rec:
						self.vwr.write(self.frame)
			cv2.waitKey(1)
		elif DEV in (3, 4):
			ret, self.frame = self.ffh.read()
			if not ret:
				print("Failed to get image from camera, something is wrong")
			cv2.waitKey(1)
		else:
			raise IOError("Invalid Hardware Selected")
		self.framecnt += 1
		if LOGS:
			gitt = time.time()-start
			if gitt > 0.5:
				print("getimgtime: ", str(gitt), "at", str(time.time()))
		return
	def surfit(self):
		"""
		Converts the current image stored in the frame buffer to a pygame surface that fits the
		screen.  Different methods are required for different input mechanisms.  No params, no
		returns.
		"""
		if DEV == 0:
			self.surf = pygame.image.frombuffer(self.rgb[0:self.rln], (800, 600), 'RGBA')
			self.surf = pygame.transform.scale(self.surf, (QWID, QHEI))
		elif DEV in (1, 2):
			self.surf = cv2.resize(self.frame, (800, 600))
			#self.surf = self.surf.torstring()
			self.surf = cv2.cvtColor(self.surf, cv2.COLOR_BGR2RGB)
			self.surf = pygame.image.frombuffer(self.surf, (800, 600), 'RGB')
			self.surf = pygame.transform.scale(self.surf, (QWID, QHEI))
		elif DEV in (3, 4):
			self.surf = cv2.resize(self.frame, (800, 600))
			self.surf = cv2.cvtColor(self.surf, cv2.COLOR_BGR2RGB)
			self.surf = pygame.image.frombuffer(self.surf, (800, 600), 'RGB')
			self.surf = pygame.transform.scale(self.surf, (QWID, QHEI))
		else:
			raise IOError("Invalid Hardware Selected")
		return
	def procimg(self):
		"""
		Process the image stored in the local pygame surface to a black and white np array.
		Use this np array to determine the center of the bright spot on the frame, then determine
		the difference from that point to the true frame center.

		:returns: - diffx - The directional difference of the reported central bright spot of the
		image to the true center of the frame in the 'x' direction.
		- diffy - The directional difference of the reported central bright spot of the image to
		the true center of the frame in the 'y' direction.
		- ratio - The percentage brightness ratio of white pixels to black pixels.
		"""
		if LOGS:
			start = time.time()
		prd = pygame.surfarray.array3d(self.surf)
		prd = np.dot(prd[:, :, :3], [0.299, 0.587, 0.114])
		prd = np.repeat(prd, 3).reshape((QWID, QHEI, 3))
		prd = np.where(prd < self.imgthresh, 0, 255)
		if LOGS:
			pftt = time.time()-start
			if pftt > 0.5:
				print("procfunctime: ", str(pftt), "at", str(time.time()))
		self.oldx = float(np.nanmean(np.nonzero(np.sum(prd, axis=1))))
		self.oldy = float(np.nanmean(np.nonzero(np.sum(prd, axis=0))))
		diffx = self.cenx - int(self.cenx*0.2) - self.oldx  #horz center of frame - moon
		diffy = self.ceny - self.oldy  #vert center of frame - moon
		ratio = np.sum(prd, dtype=np.int32)/self.prerat     #ratio of white:black
		if LOGS:
			print("ratio ", ratio)
			print("hdiff: ", self.cenx, "-", self.oldx, "=", diffx)
			print("vdiff: ", self.ceny, "-", self.oldy, "=", diffy)
		return diffx, diffy, ratio
	def procimg_dumb(self):
		"""
		Process the image stored in the local pygame surface to a black and white np array.  Only
		output the image.

		:returns: - prd - the thresholded image product (black and white np array)
		"""
		if LOGS:
			start = time.time()
		prd = pygame.surfarray.array3d(self.surf)
		prd = np.dot(prd[:, :, :3], [0.299, 0.587, 0.114])
		prd = np.repeat(prd, 3).reshape((QWID, QHEI, 3))
		prd = np.where(prd < self.imgthresh, 0, 255)
		if LOGS:
			pftt = time.time()-start
			if pftt > 0.5:
				print("procfunctime: ", str(pftt), "at", str(time.time()))
		return prd
	def img_segue(self):
		"""Creates an image which displays the computer vision version of the video stream
		"""
		SCREEN.blit(self.surf, (QWID, 0))
		return
	def holdsurf(self):
		"""This function presents the surface from getimg
		"""
		if LOGS:
			start = time.time()
		surf = self.procimg_dumb()
		surf = pygame.surfarray.make_surface(surf)
		self.drawtarget()
		if LOGS:
			sftt = time.time()-start
			if sftt > 0.5:
				print("surftime: ", str(sftt), "at", str(time.time()))
		return surf
	def get_exposure_folder(self):
		"""Fetch the camera exposure and print it to a file.  This is necessary to determine the
		fps of the video captured
		"""
		import uuid
		if DEV == 0:
			value = str(self.camera.exposure_speed) + "\n"
		elif DEV in (1, 2):
			value = str(self.get_v4l2_cam(12), 'UTF-8') + "\n"
		elif DEV in (3, 4):
			value = "N/A, exposure set on ActionCam\n"
		else:
			raise IOError("Invalid Hardware Selected")
		folder = self.folder + "/" + str(int(self.start)) + "exposure.txt"
		with open(folder, "w") as fff:
			fff.write(value + "\n")
			fff.write("starttime: " + str(int(self.start)) + "\n")
			fff.write("startframe: " + str(self.framecnt) + "\n")
			fff.write("UUID: " + str(uuid.getnode()) + "\n")
			if DEV == 0:
				pass
			if DEV in (1, 2):
				fff.write("Camera Control Values:\n")
				for i in self.clist:
					try:
						ppp = subprocess.check_output(["v4l2-ctl", "-d", self.camstring, \
							"-C", i]).decode('utf-8')
						fff.write("    " + str(ppp) + "\n")
					except subprocess.CalledProcessError:
						fff.write("    " + "clist entry not valid for this camera\n")
			elif DEV in (3, 4):
				pass
			else:
				raise IOError("Invalid Hardware Selected")
		return
	def clear_mem(self):
		"""
		Call this function to clear most of the weighty variables and collect garbage
		"""
		import gc
		self.frame = None
		gc.collect()
		return
	#def get_thresh(self):
		#"""returns threshold value
		#"""
		#return self.imgthresh
	#def set_thresh(self, val):
		#"""sets threshold value
		#"""
		#self.imgthresh = val
		#return
	#def get_iso(self):
		#"""returns the iso value
		#"""
		#return self.iso
	def set_iso(self, val):
		"""sets the iso value
		"""
		if DEV == 0:
			self.iso = val
			self.camera.iso = self.iso
		return self.iso
	def get_exp(self):
		"""
		Returns the exposure value appropriate to the hardware.

		:returns: - ret - The exposure value reported by the camera firmware.
		"""
		import re
		if DEV == 0:
			ret = self.camera.exposure_speed
		elif DEV in (1, 2):
			ret = subprocess.check_output(["v4l2-ctl", "-d", self.camstring, "-C",\
				self.clist[12]]).decode()
			ret = int(re.sub('[^0-9]', '', ret))
		elif DEV in (3, 4):
			ret = 0
		return ret
	def set_exp(self, val):
		"""
		Sets the exposure of the camera in an appropriate manner for the declared hardware

		:param val: Value which the exposure should be set to.
		:returns: - ret - Confirmation value.  This should be exactly the same as what you put
		in.
		"""
		if DEV == 0:
			self.camera.shutter_speed = val
			ret = self.get_exp()
		elif DEV in (1, 2):
			self.set_v4l2_cam(12, val)
			print("set via v4l2")
			#self.camera.set(cv2.CAP_PROP_EXPOSURE, val)
			#print("set via cv2")
			ret = self.get_exp()
		elif DEV in (3, 4):
			ret = 0
		else:
			raise IOError("Invalid Hardware Selected")
		return ret
	#def converter(self):
		#"""A simple image converter using PIL.
		#"""
		#print("centered")
		#img = self.Image.open(self.stream)
		#img = img.convert('L')
		##img = img.point(lambda x: 0 if x < 20 else 255, '1')
		##img.save("tmp.png")
		##os.system("xdg-open tmp.png") #display image - for debugging only
		#time.sleep(3)
		##os.system("killall gpicview")
		#return
	def drawtarget(self):
		"""
		Experimental function to draw a target reticle on the processed image to indicate the
		central bright spot of the averaged b/w image.
		"""
		from math import isnan
		self.procimg()
		if isnan(self.oldx):
			self.oldx = 0
		if isnan(self.oldy):
			self.oldy = 0
		print(QWID, self.oldy, SWID, self.oldy)
		print(QWID + self.oldx, QHEI, QWID + self.oldx, SHEI)
		pygame.draw.line(SCREEN, RED, [QWID, self.oldy], [SWID, self.oldy], 2)
		pygame.draw.line(SCREEN, RED, [QWID + self.oldx, 0], [QWID + self.oldx, QHEI], 2)
		return
	def stopvid(self, arg=False):
		"""stop video and print time
		:param arg: - causes camera to be released completely for USB conditions.
		"""
		stop = str(time.time())
		if DEV == 0:
			self.camera.stop_recording()
		elif DEV in (1, 2):
			if ASYNC:
				self.camera.stop()
			elif arg:
				self.camera.release()
			try:
				self.vwr.release()
			except AttributeError:
				pass
		elif DEV in (3, 4):
			self.ffh.killcamera()
		else:
			raise IOError("Invalid Hardware Selected")
		with open(self.folder + "/" + str(int(self.start)) + "exposure.txt", "a") as fff:
			fff.write("stoptime: " + stop + "\n")
			fff.write("stopframe: " + str(self.framecnt) + "\n")
		return


class ManualAdjust():
	"""
	Defines behavior and pygame GUI for the manual control stage
	"""
	if DEV == 0:
		bgj = 1000
		ltl = 100
	elif DEV in (1, 2):
		bgj = 100
		ltl = 10
	elif DEV in (3, 4):
		pass
	else:
		raise IOError("Invalid Hardware Selected")
	def __init__(self):
		"""
		:param mrgn: Margin around text to act as padding
		:param ftsz: Font size in points
		"""
		self.mrgn = 10
		self.ftsz = 25
		self.cenx, self.ceny = QWID/4, QHEI/4
		return
	def main_screen(self, lcf):
		"""
		Directions to the user
		"""
		from math import pi
		pygame.display.set_caption('Manual control')
		lctn = self.mrgn + self.ftsz
		SCREEN.blit(FONT.render('-----------MANUAL  CONTROL-----------', True, RED),\
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('Use arrow keys to move view.', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [SPACEBAR] - stop motors', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [ENTER] or [r] - track & record', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [v] - Check Computer Vision', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [i] - Cycle camera ISO mode', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [g] - Increase exposure', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [b] - Decrease exposure', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [h] - Fine increase exposure', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [n] - Fine decrease exposure', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [p] - Clear Night threshold', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('-------------------------------------', True, RED), \
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		if DEV == 0:
			SCREEN.blit(FONT.render('ISO: ' + str(lcf.iso), True, RED), (self.mrgn, lctn))
		elif DEV in (1, 2, 3, 4):
			SCREEN.blit(FONT.render('ISO: N/A', True, RED), (self.mrgn, lctn))
		else:
			raise IOError("Invalid Hardware Selected")
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('Exp: ' + str(lcf.get_exp()), True, RED), (self.mrgn, lctn))
		pygame.draw.arc(SCREEN, RED, [\
			QWID + int(self.cenx*0.3), \
			int(1*QHEI/6), \
			int(QWID/2), \
			int(QHEI/1.5)], \
			0, 2*pi, 1)
		pygame.display.update()
		return
	def update_run(self, lmf, lcf):
		"""
		Updates the screen with the mainscreen and handles keypress events
		"""
		trigger = True
		while trigger:
			SCREEN.fill((0, 0, 0))
			lcf.img_segue()
			lcf.getimg()
			lcf.surfit()
			start = time.time()
			self.main_screen(lcf)
			if LOGS:
				print("screenrendertime: ", str(time.time()-start))
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					lmf.motstop("B")
					trigger = False
				# check if key is pressed
				# if you use event.key here it will give you error at runtime
				if event.type == pygame.KEYDOWN:
					lmf.setdc(100, 100)
					if event.key == pygame.K_LEFT:
						lmf.setduty('B')
						lmf.motleft()
					elif event.key == pygame.K_RIGHT:
						lmf.setduty('B')
						lmf.motright()
					elif event.key == pygame.K_UP:
						lmf.setduty('A')
						lmf.motup()
					elif event.key == pygame.K_DOWN:
						lmf.setduty('A')
						lmf.motdown()
					elif event.key == pygame.K_SPACE:
						if LOGS:
							print("stop")
						lmf.motstop("B")
					elif event.key == pygame.K_q:
						raise SystemExit("quitting tracker")
					elif event.key == pygame.K_i:
						if DEV not in (3, 4):
							iso = lcf.iso
							if iso < 800:
								iso = iso * 2
							else:
								iso = 100
							#lcf.camera.iso = iso
							#lcf.iso = iso
							check = lcf.set_iso(iso)
							if check == iso:
								raise RuntimeError("failed to properly set ISO")
							if LOGS:
								print("iso set to ", iso)
					elif event.key == pygame.K_g:
						if DEV not in (3, 4):
							exp = lcf.get_exp()
							exp = exp - self.bgj
							if exp < 5:
								exp = 5
							check = lcf.set_exp(exp)
							if check != exp:
								raise RuntimeError("failed to properly set Exposure Time")
							if LOGS:
								print("exposure time set to ", exp)
					elif event.key == pygame.K_b:
						if DEV not in (3, 4):
							exp = lcf.get_exp()
							exp = exp + self.bgj
							if DEV == 0:
								if exp > 33000:
									exp = 33000
							elif DEV in (1, 2):
								if exp > 5000:
									exp = 4999
							else:
								raise IOError("Invalid Hardware Selected")
							check = lcf.set_exp(exp)
							if check != exp:
								raise RuntimeError("failed to properly set Exposure Time")
							if LOGS:
								print("exposure time set to ", exp)
					elif event.key == pygame.K_h:
						if DEV not in (3, 4):
							exp = lcf.get_exp()
							exp = exp - self.ltl
							if exp < 5:
								exp = 5
							check = lcf.set_exp(exp)
							if check != exp:
								raise RuntimeError("failed to properly set Exposure Time")
							if LOGS:
								print("exposure time set to ", exp)
					elif event.key == pygame.K_n:
						exp = lcf.get_exp()
						exp = exp + self.ltl
						if DEV == 0:
							if exp > 33000:
								exp = 33000
						elif DEV in (1, 2):
							if exp > 5000:
								exp = 4999
						elif DEV in (3, 4):
							pass
						else:
							raise IOError("Invalid Hardware Selected")
						if DEV not in (3, 4):
							check = lcf.set_exp(exp)
							if check != exp:
								raise RuntimeError("failed to properly set Exposure Time")
							if LOGS:
								print("exposure time set to ", exp)
					elif event.key == pygame.K_p:
						if DEV not in (3, 4):
							exp = self.bgj
							iso = 100
							check = lcf.set_iso(iso)
							if check == iso:
								raise RuntimeError("failed to properly set ISO")
							check = lcf.set_exp(exp)
							if check != exp:
								raise RuntimeError("failed to properly set Exposure Time")
					elif event.key == pygame.K_v:
						#_, _, _ = lcf.procimg()
						surf = lcf.holdsurf()
						SCREEN.blit(surf, (QWID, QHEI))
						pygame.display.update()
						pygame.time.wait(1500)
					elif event.key == pygame.K_r:
						if LOGS:
							print("run tracker")
						lmf.motstop("B")
						trigger = False
					elif event.key == pygame.K_RETURN:
						if LOGS:
							print("run tracker")
						lmf.motstop("B")
						trigger = False
		if LOGS:
			print("quitting manual control, switching to tracking")
		return







class TrackingMode():
	"""
	Defines behavior and pygame GUI for the moon tracking stage
	"""
	ticker = 0
	def __init__(self, lcf):
		"""
		Clear the screen on the first pass
		:param lostcount: the number of seconds the moon has been lost, default 0
		:param mrgn: Margin around text to act as padding
		:param ftsz: Font size in points
		"""
		SCREEN.fill((0, 0, 0))
		pygame.display.update()
		self.mrgn = 10
		self.ftsz = 25
		self.lostcount = 0
		self.check = 1
		self.vtstart = 0.075 * QHEI   #image offset for verticle movement
		self.htstart = 0.075 * QWID     #image offset for horizontal movement
		self.temptime = time.time()
		self.bwimg = None
		mp.Process(target=lcf.startrecord()).start()
		return
	def main_screen(self, lcf):
		"""
		Directions to the user
		"""
		SCREEN.fill((0, 0, 0))
		pygame.display.set_caption('Tracking Moon')
		lctn = self.mrgn + self.ftsz
		SCREEN.blit(FONT.render('----------------TRACKING MOON-------------', True, RED),\
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('*Buttons only work when window is selected!*', True, RED),\
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [q] - quit', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('(Or just close this window to to quit)', True, RED), \
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('(it might take a few seconds)', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [i] - Cycle camera ISO mode', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [z] - Decrease thresholding Value', True, RED), \
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [x] - Increase thresholding Value', True, RED), \
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('-------------------------------------', True, RED), \
			(self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		if DEV == 0:
			SCREEN.blit(FONT.render('ISO: ' + str(lcf.iso), True, RED), (self.mrgn, lctn))
		elif DEV in (1, 2, 3, 4):
			SCREEN.blit(FONT.render('ISO: N/A', True, RED), (self.mrgn, lctn))
		else:
			raise IOError("Invalid Hardware Selected")
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('Thresh: ' + str(lcf.imgthresh), True, RED), (self.mrgn, lctn))
		if self.ticker < 10 and self.bwimg:
			SCREEN.blit(self.bwimg, (QWID, QHEI))
		if not BLIND:
			lcf.img_segue()
			lcf.getimg(rec=True)
			lcf.surfit()
		pygame.display.update()
		#lcf.clear_mem()
	def update_run(self, lmf, lcf):
		"""
		Updates the screen with the mainscreen and handles keypress events
		"""
		trigger = True
		lmf.setdc(25, 25)
		while trigger:
			self.main_screen(lcf)
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_z:
						imgthresh = lcf.imgthresh
						if imgthresh > 10:
							lcf.imgthresh = imgthresh - 10
						if LOGS:
							print("decrease thresholding to ", imgthresh)
					elif event.key == pygame.K_x:
						imgthresh = lcf.imgthresh
						if imgthresh < 245:
							lcf.imgthresh = imgthresh + 10
						if LOGS:
							print("increase thresholding to ", imgthresh)
					elif event.key == pygame.K_q:
						trigger = False
						if LOGS:
							print("quitting tracker")
					elif event.key == pygame.K_i:
						iso = lcf.iso
						if iso < 800:
							iso = iso * 2
						else:
							iso = 100
						#lcf.camera.iso = iso
						#lcf.iso = iso
						check = lcf.set_iso(iso)
						if check == iso:
							raise RuntimeError("failed to properly set ISO")
						if LOGS:
							print("iso set to ", iso)
				if event.type == pygame.QUIT:
					trigger = False
			#check the time to restart camera every hour or so
			timecount = time.time() - lcf.start
			if timecount > 15*60:
				if LOGS:
					print("restart video")
				lcf.stopvid()
				lcf.startrecord()
			if self.ticker > 20:
				if not BLIND:
					lcf.getimg()
					lcf.surfit()
					diffx, diffy, ratio = lcf.procimg()
				else:
					lcf.getimg()
					diffx, diffy, ratio = lcf.procimg()
				if LOGS:
					print("timejump: ", time.time()-self.temptime)
				self.temptime = time.time()
				#TODO move vtstart/htstart to motor or image class.
				if (abs(diffy) > self.vtstart or abs(diffx) > self.htstart or self.check == 0):
					self.check = lmf.check_move(diffx, diffy, ratio)
				if self.check == 1:     #Moon successfully centered
					self.bwimg = lcf.holdsurf()
					if LOGS:
						print("centered")
					#pygame.time.wait(1500)
					self.ticker = 0
				if self.check == 0:       #centering in progress
					pygame.time.wait(lmf.wait_timer())  #sleep for 20ms, observed time for cycle closer to 0.5s
				if self.check == 2 or ratio < lmf.lostratio:        #moon lost, theshold too low
					self.lostcount += 1
					if LOGS:
						print("moon lost")
					time.sleep(1)
					if self.lostcount > 30:
						if LOGS:
							print("moon totally lost")
						trigger = False
			else:
				self.ticker += 1
		return


def main():
	"""
	main
	"""
	ltl = TimeLoop()
	while ltl.timeloop_running():
		pass
	SCREEN.fill((0, 0, 0))
	pygame.display.update()
	if DEV in (3, 4):
		ffh = FFmpegVideoCapture()
		rtsp = ffh.start_server()
		while True:
			if "Created RTSP Server" in rtsp.stdout.readline():
				break
		lcf = CameraFunctions(ffh)
	else:
		lcf = CameraFunctions(None)
	lmf = MotorFunctions()
	pygame.time.wait(500)
	try:
		lma = ManualAdjust()
		lma.update_run(lmf, lcf)
		ltm = TrackingMode(lcf)
		#lmf.demo_on()
		if LOGS:
			print("Screen width: ", SWID, " Quad width: ", QWID)
			print("Screen height: ", SHEI, " Quad height: ", QHEI)
			print("Horz Start: ", ltm.htstart, " Horz Stop: ", lmf.htstop)
			print("Vert Start: ", ltm.vtstart, "Vert Stop: ", lmf.vtstop)
		callcores = mp.Process(target=ltm.update_run(lmf, lcf))
		callcores.start()
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise
	finally:
		#lmf.demo_off()
		lcf.stopvid(True)
		if DEV in (3, 4):
			rtsp.kill()
		lmf.motstop("B")
		pygame.time.wait(1000)
		pygame.quit()
		lmf.cleanup()

if __name__ == "__main__":
	main()
