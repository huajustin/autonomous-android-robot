import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from adafruit_motorkit import MotorKit 
import time

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
