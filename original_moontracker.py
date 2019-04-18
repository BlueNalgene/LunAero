'''
Motor control and recording for Lunaero

Motor A is up and down
Motor B is right and left
'''

# Standard imports
import io
import os
import os.path
import sys
import time

# Non-standard imports
import pygame

# Third Party imports
import numpy as np

# Special Mode Imports
from _datetime import datetime

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
BLIND = True


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
		:param font_family: name or list of names for font (see pygame.font.match_font for precise format)
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
		'''Update the values in the box
		'''
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
				# *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
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
				pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=event_key, unicode=event_unicode))
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
		'''
		Called to get the surface
		'''
		return self.surface
	def get_text(self):
		'''
		Called to get the text string
		'''
		return self.input_string
	def get_cursor_position(self):
		'''
		Called to get the cursor position
		'''
		return self.cursor_position
	def set_text_color(self, color):
		'''
		Called to set the color of the text
		'''
		self.text_color = color
	def set_cursor_color(self, color):
		'''
		Called to set the color of the mouse cursor
		'''
		self.cursor_surface.fill(color)
	def clear_text(self):
		'''
		Called to clear the text string.
		'''
		self.input_string = ""
		self.cursor_position = 0

class TimeLoop():
	'''
	This class contains screens which ask the user to verify the time listed on the raspberry pi.
	The intended use is to provide for instances when the pi is not able to auto sync the clock
	with an internet connection, yet not use an RTC.
	'''
	tix = TextInput()
	def __init__(self):
		'''
		:param startup: Toggle switch for while loop
		:param timetuple: Empty tuple to hold time values
		:param mrgn: Margin around text to act as padding
		:param ftsz: Font size in points
		'''
		self.startup = True
		self.timetuple = ()
		self.mrgn = 10
		self.ftsz = 25

	def firstcheck(self):
		'''
		Ask the user to confirm that the time is correct
		'''
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
			hpos = QWID - round(len(thetime())/2)*(self.ftsz-self.mrgn)
			SCREEN.blit(FONT.render(str(thetime()), True, RED), (hpos, lctn))
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
						print("changing time")
						pygame.time.wait(100)
						i = 0
						while i < 6:
							timetuple += (int(self.timeinput(i)),)
							i += 1
						# Add milliseconds
						timetuple += (0,)
						print(timetuple)
						while not self.tzpick():
							pass
						self.startup = not self.startup
		return timetuple

	def timeinput(self, ith):
		'''
		Pygame.  Constructs a tuple of date values to use when setting the date and time
		'''
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
		'''
		Pygame.  Complains to the user if they input an invalid string for the date values and
		prompts them to try again.
		'''
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
		'''
		Pygame.  Multiple choice selection for timezone
		Sets the timezone when finished.
		'''
		trigger = True
		SCREEN.fill((0, 0, 0))
		lctn = self.mrgn + self.ftsz
		hpos = QWID - 22*(self.ftsz-self.mrgn)
		SCREEN.blit(FONT.render('Which timezone are you in right now?         ', True, RED), (hpos, lctn))
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

def _linux_setdate(time_tuple):
	'''
	This function sets the time of the system based on a tuple of values.
	:param time_tuple: This is the tuple which represents the target time setting.  Subvalues are:
		Year (needs to be 4 digits)
		Month (the rest are 2 digits)
		Day
		Hour
		Minute
		Second
		Millisecond
	'''
	import subprocess
	import shlex
	time_string = datetime(*time_tuple).isoformat()
	#subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
	subprocess.call(shlex.split("sudo date -s '%s'" % time_string))
	#subprocess.call(shlex.split("sudo hwclock -w"))
	return

def thetime():
	'''
	This function simply grabs the current time with the time zone and returns it.
	'''
	foobar = time.time()
	foobar = datetime.fromtimestamp(foobar)
	foobar = foobar.strftime('%Y-%m-%d %H:%M:%S')
	foobar = str(foobar) + "  " + str(time.localtime().tm_zone)
	return foobar










class MotorFunctions():
	'''Functions which are unique to the motor control system used in LunAero
	'''
	import RPi.GPIO as GPIO
	def __init__(self):
		'''Initialize the GPIO pins by associating the values of the pins we are using to variable.
		Initalize two pins with software controlled PWM with requisite duty cycles and freq.
		Start these PWM when they are ready.
		Assign values to the motion and ratio thresholds
'		'''
		# Defines the pins being used for the GPIO pins.
		print("Defining GPIO pins")
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
		freq = 10000                              # Set here instead of explicit, easy to change.
		self.pwma = self.GPIO.PWM(self.apinp, freq)   # Initialize PWM on pwmPins
		self.pwmb = self.GPIO.PWM(self.bpinp, freq)
		self.dca = 0                             # Set duty cycle variable to zero at first
		self.dcb = 0                             # Set duty cycle variable to zero at first
		self.pwma.start(self.dca)                # Start pulse width at 0 (pin held low)
		self.pwmb.start(self.dcb)                # Start pulse width at 0 (pin held low)
		self.acount = 0
		self.bcount = 0
		self.olddir = 0                          # Stores old movement direction; 1 left, 2 right
		self.aspect = QWID/QHEI
		# the moon must be displaced by this amount for movement to occur.
		self.lostratio = 0.001                   # a percentage of frame height
		self.vtstop = 0.05 * QHEI   #offset to stop vertical movement (must be < Start)
		self.htstop = 0.1 * QWID     #image offset to stop horizontal movement (must be < Start)
		return
	def loose_wheel(self):
		'''
		Gives some extra umph when changing direction for the looser horizontal gear
		'''
		print("Left Right power move")
		self.dcb = 100
		self.pwmb.ChangeDutyCycle(self.dcb)
		# Sets movement in opposite direction, remember that this will be backwards!
		if self.olddir == 1:
			self.motright()
		elif self.olddir == 2:
			self.motleft()
		pygame.time.wait(3000)
		self.dcb = 25
		self.pwmb.ChangeDutyCycle(self.dcb)
	def check_move(self, diffx, diffy, ratio):
		'''
		Check the values for the difference between x and y of the observed image to the
		perfect center of the screen and move the camera to center the image
		'''
		if ratio < self.lostratio:
			return 2
		else:
			if abs(diffx) < abs((diffy*self.aspect)):
				if abs(diffy) > self.vtstop:
					if diffy > 0:
						self.motup()
					else:
						self.motdown()
					self.speedup("Y")
					return 0
			else:
				if abs(diffx) > self.htstop:
					if diffx > 0:
						if self.olddir == 2:
							self.loose_wheel()
						self.motleft()
					else:
						if self.olddir == 1:
							self.loose_wheel()
						self.motright()
					self.speedup("X")
					return 0
			if (abs(diffx) < self.htstop and self.dcb > 0):
				self.motstop("X")
				return 0
			if (abs(diffy) < self.vtstop and self.dca > 0):
				self.motstop("Y")
				return 0
		if (abs(diffx) < self.htstop and abs(diffy) < self.vtstop):
			self.motstop("B")
			return 1
	def motstop(self, direct):
		'''
		Stops the motors in an intelligent way
		:param direct: Which directional motor are you stopping? X, Y, or Both?
		'''
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
				self.pwma.ChangeDutyCycle(self.dca)
				self.pwmb.ChangeDutyCycle(self.dcb)
				time.sleep(.005)
			self.GPIO.output(self.apin1, self.GPIO.LOW)
			self.GPIO.output(self.apin2, self.GPIO.LOW)
			self.GPIO.output(self.bpin1, self.GPIO.LOW)
			self.GPIO.output(self.bpin2, self.GPIO.LOW)
		elif direct == "Y":
			while self.dca > 0:
				self.dca = self.dca - 1
				self.pwma.ChangeDutyCycle(self.dca)
				time.sleep(.01)
			self.GPIO.output(self.apin1, self.GPIO.LOW)
			self.GPIO.output(self.apin2, self.GPIO.LOW)
		elif direct == "X":
			while self.dcb > 0:
				self.dcb = self.dcb - 1
				self.pwmb.ChangeDutyCycle(self.dcb)
				time.sleep(.01)
			self.GPIO.output(self.bpin1, self.GPIO.LOW)
			self.GPIO.output(self.bpin2, self.GPIO.LOW)
		return
	def motdown(self):
		'''
		Move motors to point scope DOWN
		'''
		print("moving down")
		self.GPIO.output(self.apin1, self.GPIO.HIGH)
		self.GPIO.output(self.apin2, self.GPIO.LOW)
		return
	def motup(self):
		'''
		Move motors to point scope UP
		'''
		print("moving up")
		self.GPIO.output(self.apin1, self.GPIO.LOW)
		self.GPIO.output(self.apin2, self.GPIO.HIGH)
		return
	def motright(self):
		'''
		Move motors to point scope RIGHT
		'''
		print("moving right")
		self.olddir = 2
		self.GPIO.output(self.bpin1, self.GPIO.HIGH)
		self.GPIO.output(self.bpin2, self.GPIO.LOW)
		return
	def motleft(self):
		'''
		Move motors to point scope LEFT
		'''
		print("moving left")
		self.olddir = 1
		self.GPIO.output(self.bpin1, self.GPIO.LOW)
		self.GPIO.output(self.bpin2, self.GPIO.HIGH)
		return
	def speedup(self, direct):
		'''
		Increase the motor speed by altering the duty cycle of the motor
		:param direct: Which motor? X or Y?
		The acount/bcount switch increases speed at a slower rate for already high speeds,
		this prevents zooming about too much.
		'''
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
			self.pwma.ChangeDutyCycle(self.dca)
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
			self.pwmb.ChangeDutyCycle(self.dcb)
			print("speedup", direct, self.dcb)
		return
	def setdc(self, ina, inb):
		'''#TODO'''
		self.dca = ina
		self.dcb = inb
		return
	def cleanup(self):
		''' Required to be called at end of program
		'''
		self.GPIO.cleanup()
		return










class CameraFunctions():
	'''This class provides the camera functions of for LunAero.
	Requires PILLOW and the default picamera package.
	'''
	import subprocess
	from PIL import Image
	import picamera
	iso = 200
	imgthresh = 125
	folder = ''
	def __init__(self):
		'''
		Initalize the camera
		Get some important values about the image from the camera
		Create some placeholders for the byte stream
		Get screen information locally and create a byte array to hold some more data.
		'''
		self.start = ''
		self.surf = ''
		# Byte streaming holder
		#self.stream = io.BytesIO()
		# Image Processing Values
		#self.imgthresh = 125
		self.lostcount = 0 #Always initialize at 0
		# Camera information
		self.camera = self.picamera.PiCamera()
		self.camera.led = False
		self.camera.video_stabilization = True
		self.camera.resolution = (1920, 1080)
		self.camera.color_effects = (128, 128) # turn camera to black and white
		#self.iso = 200
		# Image surface holder for pygame
		self.cenx, self.ceny = QWID/4, QHEI/4   #center of image
		self.prerat = float(QWID)*float(QHEI)
		self.rgb = bytearray(800 * 600 * 4)
		self.rln = len(self.rgb)
		# Fresh Image
		self.getimg()
		return
	def startrecord(self):
		'''
		Tell the picamera to start recording whatever we are looking at to file.  This outputs raw
		video with a non-standard framerate.  The framerate must be calculated from the exposure
		setting of the camera.
		'''
		self.start = time.time()
		folder = "/media/pi/MOON1/" + str(int(self.start))
		os.makedirs(folder)
		print(self.start)
		print("Preparing outfile")
		self.get_exposure_folder(folder)
		outfile = str(int(self.start)) + 'outA.h264'
		outfile = os.path.join(folder, outfile)
		print(str(outfile))
		self.camera.start_recording(outfile)
		time.sleep(1)
		return
	def getimg(self):
		'''
		Capture an image and see how close it is to center
		'''
		start = time.time()
		self.stream = io.BytesIO()
		self.camera.capture(self.stream, use_video_port=True, resize=(800, 600), format='rgba')
		self.stream.seek(0)
		self.stream.readinto(self.rgb)
		self.stream.close()
		self.surf = pygame.image.frombuffer(self.rgb[0:self.rln], (800, 600), 'RGBA')
		self.surf = pygame.transform.scale(self.surf, (QWID, QHEI))
		self.stream.close()
		print("getimgtime: ", str(time.time()-start))
		return
	def procimg(self, vals=True):
		start = time.time()
		prd = pygame.surfarray.array3d(self.surf)
		prd = np.dot(prd[:, :, :3], [0.299, 0.587, 0.114])
		prd = np.repeat(prd, 3).reshape((QWID, QHEI, 3))
		prd = np.where(prd < self.imgthresh, 0, 255)
		print("procfunctime: ", str(time.time()-start))
		if vals:
			oldx = float(np.nanmean(np.nonzero(np.sum(prd, axis=1))))
			oldy = float(np.nanmean(np.nonzero(np.sum(prd, axis=0))))
			diffx = self.cenx - oldx  #horz center of frame - moon
			diffy = self.ceny - oldy  #vert center of frame - moon
			ratio = np.sum(prd, dtype=np.int32)/self.prerat     #ratio of white:black
			print("ratio ", ratio)
			print("hdiff: ", self.cenx, "-", oldx, "=", diffx)
			print("vdiff: ", self.ceny, "-", oldy, "=", diffy)
			return diffx, diffy, ratio
		return prd
	def img_segue(self):
		'''Creates an image which displays the computer vision version of the video stream
		'''
		SCREEN.blit(self.surf, (QWID, 0))
		return
	def holdsurf(self):
		'''This function presents the surface from getimg
		'''
		start = time.time()
		surf = self.procimg(False)
		surf = pygame.surfarray.make_surface(surf)
		SCREEN.blit(surf, (QWID, QHEI))
		pygame.display.update()
		print("surftime: ", str(time.time()-start))
	def get_exposure_folder(self, folder):
		'''Fetch the camera exposure and print it to a file.  This is necessary to determine the
		fps of the video captured
		'''
		import uuid
		value = str(self.camera.exposure_speed) + "\n"
		self.folder = folder + '/exposure.txt'
		with open(self.folder, "w") as fff:
			fff.write(value + "\n")
			fff.write("starttime: " + str(time.time()))
			fff.write("UUID: " + str(uuid.getnode()))
		return
	def get_thresh(self):
		'''returns threshold value
		'''
		return self.imgthresh
	def set_thresh(self, val):
		'''sets threshold value
		'''
		self.imgthresh = val
		return
	def get_iso(self):
		'''returns the iso value
		'''
		return self.iso
	def set_iso(self, val):
		'''sets the iso value
		'''
		self.iso = val
		self.camera.iso = self.iso
		return
	def get_exp(self):
		'''returns the exposure value
		'''
		return self.camera.exposure_speed
	#def converter(self):
		#'''A simple image converter using PIL.
		#'''
		#print("centered")
		#img = self.Image.open(self.stream)
		#img = img.convert('L')
		##img = img.point(lambda x: 0 if x < 20 else 255, '1')
		##img.save("tmp.png")
		##os.system("xdg-open tmp.png") #display image - for debugging only
		#time.sleep(3)
		##os.system("killall gpicview")
		#return
	def stopvid(self):
		'''stop video and print time'''
		stop = str(time.time())
		self.camera.stop_recording()
		with open(self.folder, "a") as fff:
			fff.write("stoptime: " + stop)
		return


class ManualAdjust():
	'''Defines behavior and pygame GUI for the manual control stage
	'''
	def __init__(self):
		'''
		:param mrgn: Margin around text to act as padding
		:param ftsz: Font size in points
		'''
		self.mrgn = 10
		self.ftsz = 25
		return
	def main_screen(self, lcf):
		'''Directions to the user
		'''
		SCREEN.fill((0, 0, 0))
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
		lcf.img_segue()
		lcf.getimg()
		pygame.display.update()
		return
	def update_run(self, lmf, lcf):
		'''Updates the screen with the mainscreen and handles keypress events
		'''
		trigger = True
		while trigger:
			start = time.time()
			self.main_screen(lcf)
			print("screenrendertime: ", str(time.time()-start))
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					lmf.motstop("B")
					trigger = False
				# check if key is pressed
				# if you use event.key here it will give you error at runtime
				if event.type == pygame.KEYDOWN:
					dca = 100
					dcb = 100
					if event.key == pygame.K_LEFT:
						lmf.pwmb.ChangeDutyCycle(dca)
						lmf.motleft()
					elif event.key == pygame.K_RIGHT:
						lmf.pwmb.ChangeDutyCycle(dca)
						lmf.motright()
					elif event.key == pygame.K_UP:
						lmf.pwma.ChangeDutyCycle(dcb)
						lmf.motup()
					elif event.key == pygame.K_DOWN:
						lmf.pwma.ChangeDutyCycle(dcb)
						lmf.motdown()
					elif event.key == pygame.K_SPACE:
						print("stop")
						lmf.motstop("B")
					elif event.key == pygame.K_i:
						iso = lcf.iso
						if iso < 800:
							iso = iso * 2
						else:
							iso = 100
						lcf.camera.iso = iso
						lcf.iso = iso
						print("iso set to ", iso)
					elif event.key == pygame.K_g:
						exp = lcf.get_exp()
						exp = exp - 1000
						lcf.camera.shutter_speed = exp
						print("exposure time set to ", exp)
					elif event.key == pygame.K_b:
						exp = lcf.get_exp()
						exp = exp + 1000
						lcf.camera.shutter_speed = exp
						print("exposure time set to ", exp)
					elif event.key == pygame.K_h:
						exp = lcf.get_exp()
						exp = exp - 100
						lcf.camera.shutter_speed = exp
						print("exposure time set to ", exp)
					elif event.key == pygame.K_n:
						exp = lcf.get_exp()
						exp = exp + 100
						lcf.camera.shutter_speed = exp
						print("exposure time set to ", exp)
					elif event.key == pygame.K_p:
						exp = 1000
						iso = 100
						lcf.camera.iso = iso
						lcf.camera.shutter_speed = exp
					elif event.key == pygame.K_v:
						#_, _, _ = lcf.procimg()
						lcf.holdsurf()
						pygame.time.wait(1500)
					elif event.key == pygame.K_r:
						print("run tracker")
						lmf.motstop("B")
						trigger = False
					elif event.key == pygame.K_RETURN:
						print("run tracker")
						lmf.motstop("B")
						trigger = False
		print("quitting manual control, switching to tracking")
		return







class TrackingMode():
	'''Defines behavior and pygame GUI for the moon tracking stage
	'''
	ticker = 0
	def __init__(self):
		'''
		Clear the screen on the first pass
		:param lostcount: the number of seconds the moon has been lost, default 0
		:param mrgn: Margin around text to act as padding
		:param ftsz: Font size in points
		'''
		SCREEN.fill((0, 0, 0))
		pygame.display.update()
		self.mrgn = 10
		self.ftsz = 25
		self.lostcount = 0
		self.check = 1
		self.vtstart = 0.085 * QHEI   #image offset for verticle movement
		self.htstart = 0.175 * QWID     #image offset for horizontal movement
		self.temptime = time.time()
		return
	def main_screen(self, lcf):
		'''Directions to the user
		'''
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
		SCREEN.blit(FONT.render('(Or just close this window to to quit)', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('(it might take a few seconds)', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [i] - Cycle camera ISO mode', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [z] - Decrease thresholding Value', True, RED), (self.mrgn, lctn))
		lctn = lctn + self.ftsz + self.mrgn
		SCREEN.blit(FONT.render('  [x] - Increase thresholding Value', True, RED), (self.mrgn, lctn))
		if not BLIND:
			lcf.img_segue()
			lcf.getimg()
		pygame.display.update()
	def update_run(self, lmf, lcf):
		'''Updates the screen with the mainscreen and handles keypress events
		'''
		lcf.startrecord()
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
						print("decrease thresholding to ", imgthresh)
					elif event.key == pygame.K_x:
						imgthresh = lcf.imgthresh
						if imgthresh < 245:
							lcf.imgthresh = imgthresh + 10
						print("increase thresholding to ", imgthresh)
					elif event.key == pygame.K_q:
						trigger = False
						print("quitting tracker")
					elif event.key == pygame.K_i:
						iso = lcf.iso
						if iso < 800:
							iso = iso * 2
						else:
							iso = 100
						lcf.camera.iso = iso
						lcf.iso = iso
						print("iso set to ", iso)
				if event.type == pygame.QUIT:
					trigger = False
			#check the time to restart camera every hour or so
			timecount = time.time() - lcf.start
			if timecount > 40*60:
				print("restart video")
				lcf.stopvid()
				lcf.startrecord()
			if self.ticker > 20:
				if not BLIND:
					lcf.getimg()
					diffx, diffy, ratio = lcf.procimg()
				else:
					lcf.getimg()
					diffx, diffy, ratio = lcf.procimg()
				print("timejump: ", time.time()-self.temptime)
				self.temptime = time.time()
				if (abs(diffy) > self.vtstart or abs(diffx) > self.htstart or self.check == 0):
					self.check = lmf.check_move(diffx, diffy, ratio)
				if self.check == 1:     #Moon successfully centered
					lcf.holdsurf()
					print("centered")
					pygame.time.wait(1500)
					self.ticker = 0
				if self.check == 0:       #centering in progress
					pygame.time.wait(20)  #sleep for 20ms, observed time for cycle closer to 0.5s
				if self.check == 2 or ratio < lmf.lostratio:        #moon lost, theshold too low
					self.lostcount += 1
					print("moon lost")
					time.sleep(1)
					if self.lostcount > 30:
						print("moon totally lost")
						trigger = False
			else:
				self.ticker += 1
		return


def main():
	'''
	main
	'''
	while True:
		ltl = TimeLoop()
		timeval = ltl.firstcheck()
		while not timeval:
			pass
		if type(timeval) == tuple:
			_linux_setdate(timeval)
			pygame.time.wait(500)
		else:
			break
	SCREEN.fill((0, 0, 0))
	pygame.display.update()
	lcf = CameraFunctions()
	lmf = MotorFunctions()
	pygame.time.wait(500)
	try:
		lma = ManualAdjust()
		lma.update_run(lmf, lcf)
		ltm = TrackingMode()
		print("Screen width: ", SWID, " Quad width: ", QWID)
		print("Screen height: ", SHEI, " Quad height: ", QHEI)
		print("Horz Start: ", ltm.htstart, " Horz Stop: ", lmf.htstop)
		print("Vert Start: ", ltm.vtstart, "Vert Stop: ", lmf.vtstop)
		ltm.update_run(lmf, lcf)
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise
	finally:
		lmf.motstop("B")
		pygame.time.wait(1000)
		lcf.stopvid()
		with open("/home/pi/Documents/LunAero_endlog.log", 'a') as file:
			file.write(str(time.time()) + " , " + str(time.strftime('%Y-%m-%d %H:%M:%S',\
				time.localtime())) + '\n')
			file.write('\n')
			file.write(str(os.popen('journalctl -n 10 | cat').read()))
			file.write('\n')
		#os.system("killall gpicview")
		pygame.quit()
		lmf.cleanup()

if __name__ == "__main__":
	main()
