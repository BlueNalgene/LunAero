import pygame, sys
 
white = (255, 255, 255)
red = (255, 0, 0)

import RPi.GPIO as GPIO
import time

# Number of seconds to delay between sampling frames.
DELAY = 1

# Defines the pins being used for the GPIO pins.
print ("Defining GPIO pins")
GPIO.setmode(GPIO.BCM)
XPINP = 17
XPIN1 = 27
XPIN2 = 22
YPIN1 = 10
YPIN2 = 9
YPINP = 11
 
# Setup GPIO and start them with 'off' values
PINS = (XPIN1, XPIN2, XPINP, YPIN1, YPIN2, YPINP)
for i in PINS:
	GPIO.setup(i, GPIO.OUT)
	if i != XPINP or YPINP:
		GPIO.output(i, GPIO.LOW)
	else:
		GPIO.output(i, GPIO.HIGH)
		


 
pygame.init()
pygame.display.set_caption('Keyboard Example')
size = [640, 480]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
 
x = 100
y = 100
 
# using this to set the size of the rectange
# using this to also move the rectangle
step = 20
 
# by default the key repeat is disabled
# call set_repeat() to enable it
pygame.key.set_repeat(50, 50)
 
def motStop():
    print("stopping")
    GPIO.output(XPIN1, GPIO.LOW)
    GPIO.output(XPIN2, GPIO.LOW)
    GPIO.output(YPIN1, GPIO.LOW)
    GPIO.output(YPIN2, GPIO.LOW)
    dc=0                            # set dc variable t
    pwmA.ChangeDutyCycle(dc)
    pwmB.ChangeDutyCycle(dc)	
    return
 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # check if key is pressed
        # if you use event.key here it will give you error at runtime
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                print("left")
            if event.key == pygame.K_SPACE:
                print("space")
            if event.key == pygame.K_RIGHT:
                x += step
            if event.key == pygame.K_UP:
                y -= step
            if event.key == pygame.K_DOWN:
                y += step

    screen.fill(white)
 
    pygame.display.update()
    clock.tick(20)