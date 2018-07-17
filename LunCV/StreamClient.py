#!/bin/usr/python3 -B
# -*- coding: utf-8 -*-

''' Kivy module for LunAero
'''
from functools import partial
import socket
#from PIL import Image as PImage
#from threading import Thread
from kivy.core.window import Window
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
#from kivy.uix.image import Image
#from kivy.cache import Cache
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.config import Config

import pygame

Config.set('graphics', 'resizable', 0)
Window.size = (600, 500)




KIVY = '''
Main:
	BoxLayout:
		orientation: 'vertical'
		padding: root.width * 0.05, root.height * .05
		spacing: '5dp'
		BoxLayout:
			size_hint: [1,0.75]
			Image:
				id: image_source
				source: 'temp.jpg'

		BoxLayout:
			size_hint: [1,0.2]
			GridLayout:
				rows: 3
				size_hint: [0.55, 1]
				BoxLayout:
					size_hint: [1, 0.33]
					Button:
						text: ''
						background_color: 0, 0, 0, 0
					Button:
						id: upbutton
						text: '^'
						bold: True
					Button:
						text: ''
						background_color: 0, 0, 0, 0
				GridLayout:
					cols: 3
					size_hint: [1, 0.33]
					Button:
						id: leftbutton
						text: '<'
						bold: True
					Button:
						text: ''
						background_color: 0, 0, 0, 0
					Button:
						id: rightbutton
						text: '>'
						bold: True
				GridLayout:
					cols: 3
					size_hint: [1, 0.33]
					Button:
						text: ''
						background_color: 0, 0, 0, 0
					Button:
						id: downbutton
						text: 'v'
						bold: True
					Button:
						text: ''
						background_color: 0, 0, 0, 0

			BoxLayout:
				size_hint: [0.45, 1]
				Button:
					text: 'STOP MOTORS'
				Button:
					id: record_stop
					text: 'Record'
					on_press: root.rec_stop()
		BoxLayout:
			size_hint: [1, 0.05]
			GridLayout:
				cols: 3
				spacing: '10dp'
				Button:
					id: status
					text:'Camera Settings'
					bold: True
					on_press: root.cam_set()
				Button:
					text: 'Close'
					background_color: 255, 0, 0, 255
					bold: True
					on_press: root.close()
				Button:
					text: 'Adv. Networking'
					bold: True
					on_press: root.net_set()

'''
class Main(BoxLayout):
	'''This class is the support functions for the Kivy listed above
	'''
	ip_address = '192.168.5.1'
	port = 90

	def close_popup(self, btn):
		'''Closes the popup that arises during startup
		'''
		self.popup.dismiss()

	def close_popup1(self, btn):
		'''Closes the popup that arises during startup
		'''
		self.popup1.dismiss()

	def cnx(self, data):
		'''Connection handler with timeout reporting,
		works in conjunction with connect_2_pi()
		'''
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.settimeout(10)
		try:
			clientsocket.connect((self.ip_address, self.port))
			return True
		except:
			box = GridLayout(cols=1)
			box.add_widget(Label(text="TimeoutError: are you on the right network?"))
			btn = Button(text="Darn")
			btn.bind(on_press=self.close_popup1)
			box.add_widget(btn)
			self.popup1 = Popup(title='Error', content=box, size_hint=(.8, .3))
			self.popup1.open()

	def connect_2_pi(self):
		'''This function starts the socket connection with the RPi
		'''
		#clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#clientsocket.settimeout(10)
		box = GridLayout(cols=1)
		box.add_widget(Label(text="Attempting to connect to LunAero unit"))
		btn = Button(text="Cancel")
		btn.bind(on_press=self.close_popup)
		box.add_widget(btn)
		self.popup = Popup(title='Connecting to LunAero', content=box, size_hint=(.8, .3))
		self.popup.open()
		Clock.schedule_once(self.cnx, 0)
		Clock.schedule_once(self.close_popup, 0)

	def rec_stop(self):
		'''Provides functionality for starting and stopping recording
		'''
		if self.connect_test():
			if self.ids.record_stop.text == "Stop Recording":
				self.stop()
			else:
				self.ids.record_stop.text = "Stop Recording"
				Clock.schedule_interval(self.imgload, 0.3)
		else:
			self.connect_2_pi()
			return

	def stop(self):
		'''Stops the playback of images.
		'''
		self.ids.status.text = "Play"
		Clock.unschedule(self.imgload)

	def imgload(self, arg):
		'''uplodas the image during a clock event
		'''
		self.ids.image_source.reload()
		arr = Clock.get_events()
		print(len(arr))
		Clock.schedule_once(self.recv, 0)

	def recv(self, data):
		'''Socket recieve function which processes images provided by the video stream
		'''
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		buffsize = 1024
		data = b''
		if self.connect_test:
			while True:
				if len(data) < 921600:
					recvd_data = clientsocket.recv(buffsize) #need 921600
					data += recvd_data
				else:
					image = pygame.image.fromstring(data, (640, 480), 'RGB') #image from bytes
					data = b''
					pygame.image.save(image, "tmp.png")
					#self.ids.image_source.reload()
					#print(self.ids.image_source)
					#Image.reload(self.ids.image_source)
					#self.ids.image_source.reload()
					#data = b''
					#image_source.reload()
					break
		else:
			self.connect_2_pi()

	def close(self):
		'''Kills the app
		'''
		App.get_running_app().stop()

	def net_set(self):
		'''Provdes a popup for custom IP settings for advanced applications
		'''
		box = GridLayout(cols=2)
		box.add_widget(Label(text="IpAddress: ", bold=True))
		self.st = TextInput(id="serverText")
		box.add_widget(self.st)
		box.add_widget(Label(text="Port: ", bold=True))
		self.pt = TextInput(id="portText")
		box.add_widget(self.pt)
		btn = Button(text="Set", bold=True)
		btn.bind(on_press=self.ip_process)
		box.add_widget(btn)
		self.popup = Popup(title='Settings', content=box, size_hint=(.6, .4))
		self.popup.open()

	def cam_set(self):
		'''Provides a popup for important camera settings
		'''
		global EXPLABEL, EXP
		# Defining the grids
		box = GridLayout(cols=1)
		xbox = GridLayout(cols=2)
		yybox = GridLayout(cols=3)
		zzzbox = GridLayout(cols=4)

		# Layout of buttons for possible ISO settings
		zzzbox.add_widget(Label(text="Camera ISO", bold=True))
		yybox.add_widget(Button(text="0", on_press=partial(self.send_iso, 0), bold=True))
		yybox.add_widget(Button(text="100", on_press=partial(self.send_iso, 100), bold=True))
		yybox.add_widget(Button(text="200", on_press=partial(self.send_iso, 200), bold=True))
		zzzbox.add_widget(yybox)
		yybox = GridLayout(cols=3)
		yybox.add_widget(Button(text="320", on_press=partial(self.send_iso, 320), bold=True))
		yybox.add_widget(Button(text="400", on_press=partial(self.send_iso, 400), bold=True))
		yybox.add_widget(Button(text="500", on_press=partial(self.send_iso, 500), bold=True))
		zzzbox.add_widget(yybox)
		yybox = GridLayout(cols=3)
		yybox.add_widget(Button(text="640", on_press=partial(self.send_iso, 640), bold=True))
		yybox.add_widget(Button(text="800", on_press=partial(self.send_iso, 800), bold=True))
		yybox.add_widget(Button(text="1600", on_press=partial(self.send_iso, 1600), bold=True))
		zzzbox.add_widget(yybox)
		box.add_widget(zzzbox)

		# Exposure Slider.  Max value based on 1/fps estimate.
		EXP = self.get_exp()
		slid = Slider(value=EXP, min=0., max=30000., step=1)
		slid.bind(value=self.slide_value)
		EXPLABEL = Label(text="Shutter Speed: "+str(slid.value), bold=True)
		xbox.add_widget(EXPLABEL)
		xbox.add_widget(slid)
		box.add_widget(xbox)

		# This button closes the popup, sending exposure values.
		btn = Button(text="Done", bold=True)
		btn.bind(on_press=self.setting_process)
		box.add_widget(btn)

		# Finally, call the popup
		self.popup = Popup(title='Camera Settings', content=box, size_hint=(0.8, 0.6))
		self.popup.open()

	def slide_value(self, args, exp):
		'''Manages the value of the slider to be used for the exposure settings
		'''
		global EXPLABEL, EXP
		EXPLABEL.text = str(exp)
		EXP = exp

	def send_iso(self, iso, args):
		'''Sends latest ISO value to the camera
		'''
		# TODO send the ISO value to the camera
		print(iso)

	def send_exp(self):
		'''Send the exposure value to the Picamera
		'''
		# TODO send exposure value to camera
		global EXP
		print(EXP)

	def get_exp(self):
		'''Gets current exposure value from PiCamera
		'''
		#TODO get exposure value from camera
		exp = 12000
		return exp

	def setting_process(self, exp):
		'''Processes the settings from cam_set() and closes the popup
		'''
		global EXP
		self.send_exp()
		self.popup.dismiss()

	def ip_process(self, btn):
		'''Provides functionality to advanced networking options
		'''
		try:
			self.ip_address = self.st.text
			self.port = int(self.pt.text)
		except:
			pass
		self.popup.dismiss()

	def connect_test(self):
		'''A simple test to detect if the socket is still connected
		'''
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientsocket.sendall("testdata")
			return True
		except:
			print("not connected")
			return False

	def send_command(self, command):
		'''This is the magic function that sends the info to the RPi
		'''
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.sendall(command)

class VideoStreamApp(App):
	''' App builder
	'''
	def build(self):
		return Builder.load_string(KIVY)

VideoStreamApp().run()
#main.connect_2_pi()
