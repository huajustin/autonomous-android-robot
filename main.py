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
def rotateLeftInPlace(speed):
    RIGHT_MOTOR.throttle = speed
    LEFT_MOTOR.throttle = -speed
    # need to call stop() to stop rotating

# rotate the robot right in place
def rotateRightInPlace(speed):
    LEFT_MOTOR.throttle = speed
    RIGHT_MOTOR.throttle = -speed
    # need to call stop() to stop rotating

# move motors backward at defined speed
def moveBackward(speed):
    LEFT_MOTOR.throttle = -1 * speed
    RIGHT_MOTOR.throttle = -1 * speed

# stop the robot
def stop():
    LEFT_MOTOR.throttle = 0
    RIGHT_MOTOR.throttle = 0

def turnLeft(speed):
    rotateLeftInPlace(speed)
    time.sleep(0.5)
    stop()

def turnRight(speed):
    rotateRightInPlace(speed)
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
dist = 0

while True:
    lLevel = ReadChannel(lSensor) in range(800,1000)
    mLevel = ReadChannel(mSensor) in range(800,1000)
    rLevel = ReadChannel(rSensor) in range(800,1000)
    
    print("l: " + str(ReadChannel(lSensor)), end = " ")
    print("m: " + str(ReadChannel(mSensor)), end = " ")
    print("r: " + str(ReadChannel(rSensor)))
    
    if mLevel and not lLevel and not rLevel:
        dist = 0
        moveForward(moveSpeed)
        print("forward")
    elif mLevel and lLevel and not rLevel:
        dist = 0
        turnLeft(moveSpeed)
        print("left")
    elif mLevel and not lLevel and rLevel:
        dist = 0
        turnRight(moveSpeed)
        print("right")
    elif not mLevel and not lLevel and not rLevel:
        print("forward no reading")
        moveForward(moveSpeed)
        dist += moveSpeed * 2 * math.pi * 3
        if dist >= 50:
            stop()
    time.sleep(delay)
    