import os
import time
import spidev
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from adafruit_motorkit import MotorKit

#############################################

# setup the motor kit
kit = MotorKit()

# define left and right motors
LEFT_MOTOR = kit.motor1
RIGHT_MOTOR = kit.motor2

# move motors forward at defined speed
def moveForward(speed):
    LEFT_MOTOR.throttle = speed
    RIGHT_MOTOR.throttle = speed

# rotate the robot left in place
def rotateLeftInPlace():
    RIGHT_MOTOR.throttle = 1.0
    LEFT_MOTOR.throttle = -1.0
    # need to call stop() to stop rotating

# rotate the robot right in place
def rotateRightInPlace():
    LEFT_MOTOR.throttle = 1.0
    RIGHT_MOTOR.throttle = -1.0
    # need to call stop() to stop rotating

# move motors backward at defined speed
def moveBackward(speed):
    LEFT_MOTOR.throttle = -1 * speed
    RIGHT_MOTOR.throttle = -1 * speed

# stop the robot
def stop():
    LEFT_MOTOR.throttle = 0
    RIGHT_MOTOR.throttle = 0

def turnLeft():
    rotateLeftInPlace()
    time.sleep(0.5)
    stop()

def turnRight():
    rotateRightInPlace()
    time.sleep(0.5)
    stop()

def turn180():
    turnLeft()
    turnLeft()

#############################################

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# Define sensor channels
channel = 0
 
# Define delay between readings
delay = 0.1

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

#############################################

while True:
    level = ReadChannel(channel)
    if level in range(980, 1000):
        moveForward(1)
    else:
        stop()
    time.sleep(delay)
    
