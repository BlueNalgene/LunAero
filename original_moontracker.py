#Motor control and recording for Lunaero

#Motor A is up and down
#Motor B is right and left

# Standard imports
import io
import os
import os.path
import time

# Non-standard imports
from PIL import Image
import pygame

# Third Party imports
import numpy as np
import picamera
import RPi.GPIO as GPIO

#os.system('sudo fake-hwclock')

lostRatio = 0.001
imgThresh = 125

lostCount = 0 #Always initialize at 0
start = time.time()

# a percentage of frame height
# the moon must be displaced by this amount for movement to occur.
vertDim = 240  #height of test images
horDim = 320     #width of test images
vertThreshStart = 0.1 * vertDim   #image offset for verticle movement
horThreshStart = 0.20 * horDim     #image offset for horizontal movement
vertThreshStop = 0.05 * vertDim   #image offset to stop trigger verticle movement (must be < Start)
horThreshStop = 0.1 * horDim     #image offset to stop horizontal movement (must be < Start)
check = 1
iso = 200

white = (255, 255, 255)

# Defines the pins being used for the GPIO pins.
print("Defining GPIO pins")
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

freq = 1000
pwmA = GPIO.PWM(APINP, freq)   # Initialize PWM on pwmPins
pwmB = GPIO.PWM(BPINP, freq)
dcA = 0                          # Set duty cycle variable to zero at first
dcB = 0                         # Set duty cycle variable to zero at first
pwmA.start(dcA)                # Start pulse width at 0 (pin held low)
pwmB.start(dcB)                # Start pulse width at 0 (pin held low)

stream = io.BytesIO()

camera = picamera.PiCamera()
camera.led = False
camera.video_stabilization = True
camera.resolution = (1920, 1080)
camera.color_effects = (128, 128) # turn camera to black and white
prev = 6



def getImg():
	#Capture an image and see how close it is to center
	global stream
	global imgThresh
#	global theImg
	stream = io.BytesIO()  #Variable to hold image
	camera.capture(stream, use_video_port=True, resize=(horDim, vertDim), format='jpeg')
	img = Image.open(stream)
	img = img.convert('L')        #convert to monochrome
	img = img.point(lambda x: 0 if x < imgThresh else 255, '1')
	img = np.asarray(img)        #convert to numeric array
#	armcol = np.sum(img, axis=0) #sum down all columns to give a vector
#	armrow = np.sum(img, axis=1) #sum across all rows to give a vector
#	armcol[armcol < 10] = 0        #quick filter to remove effects of any stray pixels
#	armrow[armrow < 10] = 0        #quick filter to remove effects of any stray pixels
	cenx, ceny = horDim/2, vertDim/2   #center of image
	diffx = cenx - float(np.nanmean(np.nonzero(np.sum(img, axis=0))))  #horizontal center of moon
	diffy = ceny - float(np.nanmean(np.nonzero(np.sum(img, axis=1))))  #vertical center of moon
	ratio = np.sum(img, dtype=np.int32)/(float(horDim)*float(vertDim))     #ratio of white:black
#	diffx = cenx - cmx  #image center x minus mass center x - if pos shift right, if negshift left
#	diffy = ceny - cmy  #image center y minus mass center y - if pos shift down, if neg shift up
	print(ratio, diffx, diffy)
	return diffx, diffy, ratio

def checkAndMove():
	diffx, diffy, ratio = getImg()
	if ratio < lostRatio:
		rtn = 2
	else:
		if abs(diffx) > horThreshStop:
			if diffx > 0:
				motLeft()
			else:
				motRight()
			speedUp("X")
		if abs(diffy) > vertThreshStop:
			if diffy > 0:
				motUp()
			else:
				motDown()
			speedUp("Y")
		if (abs(diffx) < horThreshStop and dcB > 0):
			motStop("X")
		if (abs(diffy) < vertThreshStop and dcA > 0):
			motStop("Y")
		if (abs(diffx) < horThreshStop and abs(diffy) < vertThreshStop):
			motStop("B")
			rtn = 1
		else:
			rtn = 0
	return rtn


def motStop(direct):
	global dcA
	global dcB
	print("stopping", direct)
	if direct == "B":
		while dcA > 0 or dcB > 0:
			if dcA == 100:
				dcA = 10     #quickly stop motor going full speed
			if dcB == 100:
				dcB = 10
			if dcA > 0:
				dcA = dcA - 1   #slowly stop motor going slow (tracking moon)
			if dcB > 0:
				dcB = dcB - 1
			pwmA.ChangeDutyCycle(dcA)
			pwmB.ChangeDutyCycle(dcB)
			time.sleep(.005)
		GPIO.output(APIN1, GPIO.LOW)
		GPIO.output(APIN2, GPIO.LOW)
		GPIO.output(BPIN1, GPIO.LOW)
		GPIO.output(BPIN2, GPIO.LOW)
	if direct == "Y":
		while dcA > 0:
			dcA = dcA - 1
			pwmA.ChangeDutyCycle(dcA)
			time.sleep(.01)
		GPIO.output(APIN1, GPIO.LOW)
		GPIO.output(APIN2, GPIO.LOW)
	if direct == "X":
		while dcB > 0:
			dcB = dcB - 1
			pwmB.ChangeDutyCycle(dcB)
			time.sleep(.01)
		GPIO.output(BPIN1, GPIO.LOW)
		GPIO.output(BPIN2, GPIO.LOW)
	return

def motDown():
	print("moving down")
	GPIO.output(APIN1, GPIO.HIGH)
	GPIO.output(APIN2, GPIO.LOW)
	return

def motUp():
	print("moving up")
	GPIO.output(APIN1, GPIO.LOW)
	GPIO.output(APIN2, GPIO.HIGH)
	return

def motRight():
	print("moving right")
	GPIO.output(BPIN1, GPIO.HIGH)
	GPIO.output(BPIN2, GPIO.LOW)
	return

def motLeft():
	print("moving left")
	GPIO.output(BPIN1, GPIO.LOW)
	GPIO.output(BPIN2, GPIO.HIGH)
	return

def speedUp(direct):
	global dcA
	global dcB
	if direct == "Y":
		if dcA < 20:
			dcA = 20
			pwmA.ChangeDutyCycle(dcA)
		if dcA < 70 and dcA > 19:
			dcA = dcA + 2
			pwmA.ChangeDutyCycle(dcA)
		print("speedup ", direct, dcA)
	if direct == "X":
		if dcB < 20:
			dcB = 20
			pwmB.ChangeDutyCycle(dcB)
		if dcB < 70 and dcB > 19:
			dcB = dcB + 2
			pwmB.ChangeDutyCycle(dcB)
		print("speedup", direct, dcB)
	return

def startRecording():
	global start
	start = time.time()
	print(start)
	print("Preparing outfile")
	outfile = int(time.time())
	outfile = str(outfile) + 'outA.h264'
	outfile = os.path.join('/media/pi/MOON1', outfile)
	print(str(outfile))
	camera.start_recording(outfile)
	time.sleep(1)
	return

def goPrev(prev):
	if prev == 1:
		camera.start_preview(fullscreen=False, window=(1200, -20, 640, 480))
	if prev == 2:
		camera.start_preview(fullscreen=False, window=(800, -20, 1280, 960))
	if prev == 3:
		camera.start_preview(fullscreen=False, window=(20, 400, 640, 480))
	if prev == 4:
		camera.start_preview(fullscreen=False, window=(20, 200, 1280, 960))
	if prev == 5:
		camera.start_preview(fullscreen=True)
	if prev == 6:
		camera.start_preview(fullscreen=False, window=(0,0, 640, 480))
	return



goPrev(prev)
time.sleep(2)
exp = camera.exposure_speed
print("exposure speed ", exp)

red = (255, 0, 0)
position = (620, 20)
os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])

#pygame.init()
pygame.display.init()
pygame.font.init()
#pygame.event.init()
#pygame.time.init()

pygame.display.set_caption('Manual control')
size = [640, 480]
mrgn = 10
ftsz = 25
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont('monospace', ftsz)
lctn = mrgn + ftsz
screen.blit(font.render('-----------------MANUAL  CONTROL-----------------', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('Use arrow keys to move view.', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [SPACEBAR] - stop motors', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [ENTER] or [r] - track & record', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [v] - Change preview window mode', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [i] - Cycle camera ISO mode', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [d] - Increase exposure', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [b] - Decrease exposure', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [p] - Clear Night threshold', True, red), (mrgn, lctn))
pygame.display.update()
clock = pygame.time.Clock()
x = 0

while x < 10:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			motStop("B")
			x = 100
		# check if key is pressed
		# if you use event.key here it will give you error at runtime
		if event.type == pygame.KEYDOWN:
			dcA = 100
			dcB = 100
			if event.key == pygame.K_LEFT:
				pwmB.ChangeDutyCycle(dcA)
				motLeft()
			if event.key == pygame.K_RIGHT:
				pwmB.ChangeDutyCycle(dcA)
				motRight()
			if event.key == pygame.K_UP:
				pwmA.ChangeDutyCycle(dcB)
				motUp()
			if event.key == pygame.K_DOWN:
				pwmA.ChangeDutyCycle(dcB)
				motDown()
			if event.key == pygame.K_SPACE:
				print("stop")
				motStop("B")
			if event.key == pygame.K_i:
				if iso < 800:
					iso = iso * 2
				else:
					iso = 100
				camera.iso = iso
				print("iso set to ", iso)
			if event.key == pygame.K_d:
				exp = exp - 1000
				camera.shutter_speed = exp
				print("exposure time set to ", exp)
			if event.key == pygame.K_b:
				exp = exp + 1000
				camera.shutter_speed = exp
				print("exposure time set to ", exp)
			if event.key == pygame.K_p:
				exp = 1000
				iso = 100
				camera.iso = iso
				camera.shutter_speed = exp
			if event.key == pygame.K_v:
				prev = prev + 1
				if prev > 6:
					prev = 1
				camera.stop_preview()
				goPrev(prev)
			if event.key == pygame.K_r:
				print("run tracker")
				motStop("B")
				x = 100
			if event.key == pygame.K_RETURN:
				print("run tracker")
				motStop("B")
				x = 100
print("quitting manual control, switching to tracking")

screen.fill((0, 0, 0))
pygame.display.update()
pygame.display.set_caption('Tracking Moon')
lctn = mrgn + ftsz
screen.blit(font.render('--------------------TRACKING MOON----------------', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('*Buttons only work when this window is selected!*', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [q] - quit', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('(Or just close this window to to quit)', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('(it might take a few seconds)', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [v] - Change preview window mode', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [i] - Cycle camera ISO mode', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [d] - Increase exposure', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [b] - Decrease exposure', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [z] - Decrease thresholding Value', True, red), (mrgn, lctn))
lctn = lctn + ftsz + mrgn
screen.blit(font.render('  [x] - Increase thresholding Value', True, red), (mrgn, lctn))
pygame.display.update()

startRecording()

cnt = 0
while cnt < 55:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			dcA = 50
			dcB = 50
			if event.key == pygame.K_z:
				if imgThresh > 10:
					imgThresh = (imgThresh - 10)
				print("decrease thresholding to ", imgThresh)
			if event.key == pygame.K_x:
				if imgThresh < 245:
					imgThresh = (imgThresh + 10)
				print("increase thresholding to ", imgThresh)
			if event.key == pygame.K_q:
				cnt = 100
				print("quitting tracker")
			if event.key == pygame.K_i:
				if iso < 800:
					iso = iso * 2
				else:
					iso = 100
				camera.iso = iso
				print("iso set to ", iso)
			if event.key == pygame.K_d:
				exp = exp - 100
				camera.shutter_speed = exp
				print("exposure time set to ", exp)
			if event.key == pygame.K_b:
				exp = exp + 100
				camera.shutter_speed = exp
				print("exposure time set to ", exp)
			if event.key == pygame.K_v:
				prev = prev + 1
				if prev > 6:
					prev = 1
				camera.stop_preview()
				goPrev(prev)
		if event.type == pygame.QUIT:
			cnt = 100
	now = time.time()      #check the time to restart camera every hour or so
	timeCount = now - start
	camera.annotate_text = ' ' * 100 + str(int(round(timeCount))) + 'sec'
	if timeCount > 2*60*60:
		print("restart video")
		camera.stop_recording()
		startRecording()
	diffx, diffy, ratio = getImg()
	if (abs(diffy) > vertThreshStart or abs(diffx) > horThreshStart or check == 0):
		check = checkAndMove()
	if check == 1:     #Moon successfully centered
		print("centered")
		lostCount = 0
		img = Image.open(stream)
		img = img.convert('L')
#		img = img.point(lambda x: 0 if x < 20 else 255, '1')
#		img.save("tmp.png")
#		os.system("xdg-open tmp.png") #display image - for debugging only
		time.sleep(3)
#		os.system("killall gpicview")
	if check == 0:       #centering in progress
		time.sleep(.02)  #sleep for 20ms
#		motStop("B")
	if check == 2 or ratio < lostRatio:        #moon lost, theshold too low
		lostCount = lostCount + 1
		print("moon lost")
		time.sleep(1)
		if lostCount > 30:
			print("moon totally lost")
			#os.system("killall gpicview")
			cnt = 100   #set count to 100 to exit the while loop

motStop("B")
time.sleep(2)
camera.stop_recording()
with open("/home/pi/Documents/LunAero_endlog.log", 'a') as file:
	file.write(str(time.time()) + " , " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())) + '\n')
	file.write('\n')
	file.write(str(os.popen('journalctl -n 10 | cat').read()))
	file.write('\n')
camera.stop_preview()
#os.system("killall gpicview")
pygame.quit()
GPIO.cleanup()

