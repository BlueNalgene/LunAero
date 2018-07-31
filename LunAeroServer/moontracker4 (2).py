#Motor control and recording for Lunaero

#Motor A is up and down
#Motor B is right and left

import sys
import subprocess
import os
import os.path
from scipy import ndimage
from PIL import Image
import numpy as np
import pygame, sys
import RPi.GPIO as GPIO
import time
import picamera
import io
#import matplotlib.pyplot as plt

moveFactorX = 0.0020 
moveFactorY = 0.0015
lostRatio = 0.005
imgThresh = 125

lostCount = 0 #Always initialize at 0
start = time.time()

# a percentage of frame height
# the moon must be displaced by this amount for movement to occur.
vertDim = 240  #height of test images
horDim = 320     #width of test images
vertThreshStart = 0.10 * vertDim   #image offset to start trigger verticle movement
horThreshStart = 0.20 * horDim     #image offset to start horizontal movement
vertThreshStop = 0.05 * vertDim   #image offset to stop trigger verticle movement (should be less than Start)
horThreshStop = 0.10 * horDim     #image offset to stop horizontal movement (should be less than Start)
check = 1
iso = 200

white = (255,255,255)
# Defines the pins being used for the GPIO pins.
print ("Defining GPIO pins")
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
dcA=0                          # Set duty cycle variable to zero at first
dcB=0                         # Set duty cycle variable to zero at first
pwmA.start(dcA)                # Start pulse width at 0 (pin held low)         
pwmB.start(dcB)                # Start pulse width at 0 (pin held low)  

stream = io.BytesIO()

def getImg():
    #Capture an image and see how close it is to center
    global stream
    global imgThresh
    global theImg
    stream = io.BytesIO()  #Variable to hold image
    camera.capture(stream, use_video_port=True, resize=(horDim, vertDim), format='jpeg')
    img = Image.open(stream)
    img = img.convert('L')        #convert to monochrome
    img = img.point(lambda x: 0 if x < imgThresh else 255, '1')
    arm = np.asarray(img)        #convert to numeric array
    armcol = np.sum(arm, axis = 0) #sum down all columns to give a vector
    armrow = np.sum(arm, axis = 1) #sum across all rows to give a vector
    armcol[armcol < 10] = 0        #quick filter to remove effects of any stray pixels
    armrow[armrow < 10] = 0        #quick filter to remove effects of any stray pixels
    cmx = np.mean(np.nonzero(armcol))  #horizontal center of moon 
    cmy = np.mean(np.nonzero(armrow))  #vertical center of moon 
    ##width, height = img.size     #get image size parameters
    cenx, ceny = horDim/2, vertDim/2   #center of image
    #cmy, cmx = ndimage.measurements.center_of_mass(arm)  #Center of mass
    #percent = height/100         #
        #arm = arm.sum()                #sum of all 1s in image - used to determin if the moon is lost
    
    
    ratio = arm.sum()/(horDim*vertDim)     #ratio of white to black - used to tell if the moon is lost
    diffx = cenx - cmx  #image center x minus mass center x - if positive shift right, if negative shift left
    diffy = ceny - cmy  #image center y minus mass center y - if positive shift down, if negative shift up
    print(ratio, cmx, cmy, diffx, diffy)
    return diffx, diffy, ratio

def checkAndMove():
    diffx, diffy, ratio = getImg()
    if ratio < lostRatio:
        rtn= 2                #returned value of 2 indicates moon is lost.
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
            

def motStop(dir):
    global dcA
    global dcB
    print("stopping", dir)
    if dir == "B":
        while (dcA > 0 or dcB > 0):
            if dcA == 100: dcA = 10     #quickly stop motor going full speed
            if dcB == 100: dcB = 10
            if dcA > 0: dcA = dcA - 1   #slowly stop motor going slow (tracking moon)
            if dcB > 0: dcB = dcB - 1
            pwmA.ChangeDutyCycle(dcA)
            pwmB.ChangeDutyCycle(dcB)
            time.sleep(.005)
        GPIO.output(APIN1, GPIO.LOW)
        GPIO.output(APIN2, GPIO.LOW)
        GPIO.output(BPIN1, GPIO.LOW)
        GPIO.output(BPIN2, GPIO.LOW)
    if dir == "Y":
        while (dcA > 0):
            dcA = dcA - 1
            pwmA.ChangeDutyCycle(dcA)
            time.sleep(.01)
        GPIO.output(APIN1, GPIO.LOW)
        GPIO.output(APIN2, GPIO.LOW)
    if dir == "X":
        while (dcB > 0):
            dcB = dcB - 1
            pwmB.ChangeDutyCycle(dcB)
            time.sleep(.01)
        GPIO.output(BPIN1, GPIO.LOW)
        GPIO.output(BPIN2, GPIO.LOW)
    return

def motUp():
    print("moving up")
    GPIO.output(APIN1, GPIO.HIGH)
    GPIO.output(APIN2, GPIO.LOW)
    #GPIO.output(APINP, GPIO.HIGH)
    return

def motDown():
    print("moving down")
    GPIO.output(APIN1, GPIO.LOW)
    GPIO.output(APIN2, GPIO.HIGH)
    #GPIO.output(APINP, GPIO.HIGH)
    return

def motLeft():
    print("moving left")
    GPIO.output(BPIN1, GPIO.HIGH)
    GPIO.output(BPIN2, GPIO.LOW)
    #GPIO.output(BPINP, GPIO.HIGH)
    return

def motRight():
    print("moving right")
    GPIO.output(BPIN1, GPIO.LOW)
    GPIO.output(BPIN2, GPIO.HIGH)
    #GPIO.output(BPINP, GPIO.HIGH)
    return

def speedUp(dir):
##    global pwmA
##    global pwmB
    global dcA
    global dcB
    if dir == "Y":
        if dcA < 50: 
            dcA = dcA + 2
            pwmA.ChangeDutyCycle(dcA)
        print("speedup ", dir, dcA)
    if dir == "X":
        if dcB < 50:
            dcB = dcB + 2
            pwmB.ChangeDutyCycle(dcB)
        print("speedup", dir, dcB)
    return

##def slowDown(dir):
##    global dcA
##    global dcB
##    if dir == "Y":
##        if dcA > 0: 
##            dcA = dcA - 2
##            pwmA.ChangeDutyCycle(dcA)
##        print("slowdown ", dir, dcA)
##    if dir == "X":
##        if dcB > 0:
##            dcB = dcB - 2
##            pwmB.ChangeDutyCycle(dcB)
##        print("slowdown ", dir, dcB)
##    return


def startRecording():
    global start
    start = time.time()
    print(start)
    print ("Preparing outfile")
    outfile = int(time.time())
    outfile = str(outfile) + 'outA.h264'
    outfile = os.path.join('/media/pi/MOON1', outfile)
    print (str(outfile))
    camera.start_recording(outfile)
    time.sleep(1)
    return

def goPrev(prev):
    if prev == 1: camera.start_preview(fullscreen = False, window = (1200,-20,640,480))
    if prev == 2: camera.start_preview(fullscreen = False, window = (800,-20,1280,960))
    if prev == 3: camera.start_preview(fullscreen = False, window = (20,400,640,480))
    if prev == 4: camera.start_preview(fullscreen = False, window = (20,200,1280,960))
    if prev == 5: camera.start_preview(fullscreen = True)
    return

camera = picamera.PiCamera()
camera.video_stabilization = True
camera.resolution = (1920, 1080)
camera.color_effects = (128,128) # turn camera to black and white
prev = 3
goPrev(prev)
time.sleep(2)
exp = camera.exposure_speed
print("exposure speed ", exp)

pygame.init()
pygame.display.set_caption('Manual control')
size = [400, 240]
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont('Arial', 25)
screen.blit(font.render('Use arrow keys to move.', True, (255,0,0)), (25, 25))
screen.blit(font.render('Hit the space bar to stop.', True, (255,0,0)), (25, 75))
screen.blit(font.render('Press ENTER or r to run the', True, (255,0,0)), (25, 125))
screen.blit(font.render('moon tracker', True, (255,0,0)), (25, 165))
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
                print("left")
                pwmB.ChangeDutyCycle(dcA)
                motLeft()     
            if event.key == pygame.K_RIGHT:
                print("right")
                pwmB.ChangeDutyCycle(dcA)
                motRight()
            if event.key == pygame.K_UP:
                print("up")
                pwmA.ChangeDutyCycle(dcB)
                motUp()
            if event.key == pygame.K_DOWN:
                print("down")
                pwmA.ChangeDutyCycle(dcB)
                motDown()
            if event.key == pygame.K_SPACE:
                print("stop")
                motStop("B")
            if event.key == pygame.K_i:
                if (iso < 800):
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
            if event.key == pygame.K_v:
                prev = prev + 1
                if prev > 5: prev = 1
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
#pygame.quit()
#GPIO.cleanup()
print("quitting manual control, switching to tracking")
#sys.exit()
#print("continue")
#pygame.display.quit()

screen.fill((0,0,0))
pygame.display.update()
pygame.display.set_caption('Tracking Moon')
screen.blit(font.render('TRACKING MOON.', True, (255,0,0)), (25, 25))
screen.blit(font.render('Click this window and type "q" to quit', True, (255,0,0)), (25, 75))
screen.blit(font.render('Or just close this window to to quit.', True, (255,0,0)), (25, 125))
screen.blit(font.render('(it might take a few seconds)', True, (255,0,0)), (25, 175))
pygame.display.update()


##print ("Preparing outfile")
##outfile = int(time.time())
##outfile = str(outfile) + 'outA.h264'
##outfile = os.path.join('/media/pi/MOON1', outfile)
##print (str(outfile))
##camera.start_recording(outfile)
##time.sleep(1)

startRecording()   #make sure this is enabled!!!!!!!!!!!!!!!!

cnt = 0
while cnt < 55:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                if (imgThresh > 10): imgThresh = (imgThresh - 10)
                print("decrease thresholding to ", imgThresh)
            if event.key == pygame.K_x:
                if (imgThresh < 245): imgThresh = (imgThresh + 10)
                print("increase thresholding to ", imgThresh)
            if event.key == pygame.K_q:
                cnt = 100
                print("quitting tracker")
            if event.key == pygame.K_i:
                if (iso < 800):
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
                if prev > 5: prev = 1
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
    if check == 1:       #Moon successfully centered
        print("centered")
        lostCount = 0
        img = Image.open(stream)
        #img = img.convert('L')
        #img = img.point(lambda x: 0 if x < 20 else 255, '1')
        img.save("tmp.png")
        os.system("xdg-open tmp.png") #display image - for debugging only
        time.sleep(3)
        os.system("killall gpicview")
    if check == 0:       #centering in progress
        time.sleep(.02)  #sleep for 20ms
    if (check == 2 or ratio < lostRatio):        #moon lost, theshold too low
        lostCount = lostCount + 1
        print ("moon lost")
        time.sleep(1)
        if lostCount > 30:
            print("moon totally lost")
            #os.system("killall gpicview")
            cnt = 100   #set count to 100 to exit the while loop
    
       
time.sleep(2)
motStop("B")
camera.stop_recording()
os.system("killall gpicview")  #remove pics from screen if there are any
camera.stop_preview()
pygame.quit() 
GPIO.cleanup()