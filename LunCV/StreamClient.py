from PIL import Image as PImage

from kivy.config import Config
Config.set('graphics','resizable',0)

from kivy.core.window import Window
Window.size = (600, 500)


from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import socket
from threading import *
from kivy.uix.image import Image
from kivy.cache import Cache
import pygame
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
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
				cols: 4
				spacing: '10dp'
				Button:
					id: status
					text:'Play'
					bold: True
					on_press: root.playPause()
				Button:
					text: 'Close'
					bold: True
					on_press: root.close()
				Button:
					text: 'Setting'
					bold: True
					on_press: root.setting()
				Button:
					text: 'Login'
					bold: True
					on_press: root.ssh_creds()

'''
class main(BoxLayout):
	ipAddress = '192.168.5.1'
	port = 90
	user_name = None
	pass_word = None

	def ssh_process(self, btn):
		try:
			self.user_name = self.un.text
			self.pass_word = self.pw.text
		except:
			pass
		self.popup.dismiss()
		self.ssh_login()

	def ssh_creds(self):
		arr = Clock.get_events()
		print(len(arr))

	def ssh_login(self):
		import paramiko
		command = 'python $HOME/Downloads/LunAero/moontracker2.py'
		if self.user_name == None or self.pass_word == None:
			box = GridLayout(cols=1)
			box.add_widget(Label(text="Enter your Username/Password"))
			btn = Button(text="OK")
			btn.bind(on_press=self.closePopup)
			box.add_widget(btn)
			self.popup1 = Popup(title='Error',content=box,size_hint=(.8,.3))
			self.popup1.open()
		elif self.ipAddress == None:
			box = GridLayout(cols=1)
			box.add_widget(Label(text="Ip Not Set"))
			btn = Button(text="OK")
			btn.bind(on_press=self.closePopup)
			box.add_widget(btn)
			self.popup1 = Popup(title='Error',content=box,size_hint=(.8,.3))
			self.popup1.open()
		else:
			try:
				self.ssh_creds()
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(ipAddress, username=user_name, password=pass_word)
				ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
			except paramiko.AuthenticationException:
				print("Bad credentials")
			except paramiko.SSHException:
				print("Issues with SSH service")
			except socket.error:
				print("Device Unreachable")
			finally:
				ssh.close()

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
				Clock.schedule_interval(self.imgload, 0.3)

	def closePopup(self,btn):
		self.popup1.dismiss()

	def stop(self):
		self.ids.status.text = "Play"
		Clock.unschedule(self.imgload)

	def imgload(self, arg):
		self.ids.image_source.reload()
		arr = Clock.get_events()
		print(len(arr))
		Clock.schedule_once(self.recv, 0)

	def recv(self, dt):
		clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.connect((self.ipAddress, self.port))
		buffsize = 1024
		data = b''
		while True:
			if len(data) < 921600:
				recvd_data = clientsocket.recv(buffsize) #need 921600
				data += recvd_data
				print(len(data))
				pass
			else:
				print len(data)
				#image = PImage.frombytes("RGB", (640, 480), data, "raw", 'RGB', 0, 1) #image from bytes
				image = pygame.image.fromstring(data, (640, 480), 'RGB') #image from bytes
				data = b''
				pygame.image.save(image, "temp.jpg")
				#self.ids.image_source.reload()
				#print(self.ids.image_source)
				#Image.reload(self.ids.image_source)
				#self.ids.image_source.reload()
				#data = b''
				#image_source.reload()
				break

	def close(self):
		App.get_running_app().stop()

#[12:31] <tshirtman> Guest24702: hm, recv is blocking right? you should put it in a thread rather than in a clock event
#[12:31] == kuzeyron [~kuzeyron@host-121-25.parnet.fi] has joined #kivy
#[12:31] <tshirtman> you'll need to trigger the reload through a clock event though, to avoid opengl issues

	def setting(self):
		box = GridLayout(cols = 2)
		box.add_widget(Label(text="IpAddress: ", bold = True))
		self.st = TextInput(id= "serverText")
		box.add_widget(self.st)
		box.add_widget(Label(text="Port: ", bold = True))
		self.pt = TextInput(id= "portText")
		box.add_widget(self.pt)
		btn = Button(text="Set", bold=True)
		btn.bind(on_press=self.settingProcess)
		box.add_widget(btn)
		self.popup = Popup(title='Settings',content=box,size_hint=(.6,.4))
		self.popup.open()

	def settingProcess(self, btn):
		try:
			self.ipAddress = self.st.text
			self.port = int(self.pt.text)
		except:
			pass
		self.popup.dismiss()


class videoStreamApp(App):
    def build(self):
        return Builder.load_string(kv)

videoStreamApp().run()
