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
		


time.sleep(1)
print("crankng both")
freq = 1000
pwmA = GPIO.PWM(XPINP, freq)   # Initialize PWM on pwmPin 
pwmB = GPIO.PWM(YPINP, freq) 
GPIO.output(XPIN1, GPIO.LOW)
GPIO.output(XPIN2, GPIO.HIGH)
GPIO.output(YPIN2, GPIO.LOW)
GPIO.output(YPIN1, GPIO.HIGH)
dc=100                          # set dc variable
pwmA.start(dc)                      
pwmB.start(dc)

time.sleep(5)

print("stopping")
GPIO.output(XPIN1, GPIO.LOW)
GPIO.output(XPIN2, GPIO.LOW)
GPIO.output(YPIN1, GPIO.LOW)
GPIO.output(YPIN2, GPIO.LOW)
dc=0                            # set dc variable t
pwmA.ChangeDutyCycle(dc)
pwmB.ChangeDutyCycle(dc)	
pwmA.stop()
pwmB.stop()

GPIO.cleanup() 
		