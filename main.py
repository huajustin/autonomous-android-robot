import os
import time
import math
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
lSensor = 0
mSensor = 1
rSensor = 2
moveSpeed = 0.25
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
    lLevel = ReadChannel(lSensor) in range(980, 1000)
    mLevel = ReadChannel(mSensor) in range(980, 1000)
    rLevel = ReadChannel(rSensor) in range(980, 1000)
    if mLevel and not lLevel and not rLevel:
        moveForward(moveSpeed)
    elif mLevel and lLevel and not rLevel:
        turnLeft()
    elif mLevel and not lLevel and rLevel:
        turnRight()
    elif not mLevel and not lLevel and not rLevel:
        dist = 0
        while dist < 3:
            moveForward(moveSpeed)
            dist += moveSpeed * 2 * pi * 3
        if dist >= 3:
            stop()
    time.sleep(delay)
    
