import socket
import pygame
from threading import *

from kivy.config import Config
Config.set('graphics','resizable',0)

from kivy.core.window import Window
Window.size = (600, 500)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button

kv = '''
main:
	BoxLayout:
		orientation: 'vertical'
		padding: root.width * 0.05, root.height * .05
		spacing: '5dp'
		BoxLayout:
			size_hint: [1,.85]
			Image:
				id: image_source
				source: 'temp.jpg'
		BoxLayout:
			size_hint: [1,.15]
			GridLayout:
				cols: 1
				spacing: '10dp'
				Button:
					id: status
					text:'Play'
					bold: True
					on_press: root.playPause()

'''
class main(BoxLayout):
	ipAddress = '192.168.5.1'
	port = 90
	user_name = None
	pass_word = None

	def playPause(self):
		if self.ipAddress == None or self.port == None:
			box = GridLayout(cols=1)
			box.add_widget(Label(text="Ip or Port Not Set"))
			btn = Button(text="OK")
			btn.bind(on_press=self.closePopup)
			box.add_widget(btn)
			self.popup1 = Popup(title='Error',content=box,size_hint=(.8,.3))
			self.popup1.open()
		else:
			if self.ids.status.text == "Stop":self.stop()
			else:
				self.ids.status.text = "Stop"
				Clock.schedule_interval(self.recv, 0.1)

	def closePopup(self,btn):
		self.popup1.dismiss()

	def stop(self):
		self.ids.status.text = "Play"
		Clock.unschedule(self.recv)

	def recv(self, dt):
		clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.connect((self.ipAddress, self.port))
		buffsize = 1024
		data = b''
		while True:
			recvd_data = clientsocket.recv(buffsize) #need 921600
			data += recvd_data
			if len(data) < 921600:
				pass
			else:
				image = pygame.image.fromstring(data, (640, 480), 'RGB') #image from bytes
				data = b''
				pygame.image.save(image, "temp.jpg")
				self.ids.image_source.reload()
				data = b''

	def close(self):
		App.get_running_app().stop()

class videoStreamApp(App):
    def build(self):
        return Builder.load_string(kv)

videoStreamApp().run()
