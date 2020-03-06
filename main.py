import os
import time
import math
import spidev
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from adafruit_motorkit import MotorKit
from http.server import BaseHTTPRequestHandler, HTTPServer
from picamera import PiCamera

#############################################
# Motor definitions and functions
#############################################

# setup the motor kit
kit = MotorKit()

# define left and right motors
LEFT_MOTOR = kit.motor1
RIGHT_MOTOR = kit.motor2

# move motors forward at defined speed
def moveForward(speed):
    LEFT_MOTOR.throttle = speed * 1.1
    RIGHT_MOTOR.throttle = speed
    
def nudge(speed):
    moveForward(speed)
    time.sleep(0.1)
    
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
    #stop()

def turnRight(speed):
    rotateRightInPlace(speed)
    time.sleep(0.5)
    #stop()

def turn180():
    turnLeft()
    turnLeft()

#############################################
# Sensor/spidev definitions and functions
#############################################

# setting up spi
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# Define sensor channels
lSensor = 0
mSensor = 1
rSensor = 2

# Define delay between readings
delay = 0.1

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

#############################################
# Web server definitions and functions
#############################################

host_name = '137.82.226.231'    # Change this to Raspberry Pi IP address
host_port = 8000

class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        # generate the html web with four buttons to control the robot to move forward, backward, left and right
        html = '''
            <html>
            <body style="width:960px; margin: 20px auto;">
            <h1>CPEN291 Project 1 Raspberry Pi web robot control</h1>
            <p>Current temperature is {}</p>
            <form action="/" method="POST">
                Robot control: <br />
                <input type="submit" name="submit" value="Forward"> <br />
                <input type="submit" name="submit" value="Left">
                <input type="submit" name="submit" value="Right"><br />
                <input type="submit" name="submit" value="Backward"> 
            </form>
            </body>
            </html>
        '''
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))

    def do_POST(self):
        # we get the request from the user
        # call the specific function in motor functions to handle the request
        content_length = int(self.headers['Content-Length'])        # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8") # Get the data
        post_data = post_data.split("=")[1]                         # Only keep the value

        if post_data == 'Forward':
            moveForward(moveSpeed)
            print("car is moving forward")
        elif post_data == 'Backward':
            moveBackward(moveSpeed)
            print("car is moving backward")
        if post_data =='Left':
            rotateLeft(moveSpeed)
            print("car is rotating left")
        elif post_data == 'Right':
            rotateRight(moveSpeed)
            print("car is rotating right")
        
        self._redirect('/') # finished handling request, redirect back to the root url

#############################################
# Camera definitions and functions
#############################################

#camera = PiCamera()

#############################################
# Main loop function
#############################################

dist = 0
speedFactor = 0.3
moveSpeed = 0.3

try:
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
        elif mLevel and lLevel and rLevel:
            dist = 0
            moveForward(moveSpeed)
            print("cross")
        elif (mLevel and lLevel and not rLevel) or lLevel:
            dist = 0
            decayFactor = 0.5
            turnLeft(moveSpeed * .8)
            while lLevel or rLevel:
                if lLevel and not mLevel:
                    turnLeft(moveSpeed * speedFactor)
                    #break
                elif rLevel and not mLevel:
                    turnRight(moveSpeed * speedFactor * decayFactor)
                elif decayFactor <= 0:
                    break
                elif not mLevel and not lLevel and not rLevel:
                    moveBackward(0.2)
                else:
                    break
                decayFactor -= 0.1
                turnLeft(moveSpeed * decayFactor)
                #time.sleep(0.1)
                lLevel = ReadChannel(lSensor) in range(800,1000)
                rLevel = ReadChannel(rSensor) in range(800,1000)
                mLevel = ReadChannel(mSensor) in range(800,1000)
                print("LEFT: " + str(ReadChannel(lSensor)), end = " ")
                print("MIDDLE: " + str(ReadChannel(mSensor)), end = " ")
                print("RIGHT: " + str(ReadChannel(rSensor)))
                print("LEFTL00P")
            print("left")
        elif (mLevel and not lLevel and rLevel) or rLevel:
            dist = 0
            decayFactor = 0.5
            turnRight(moveSpeed * 0.8)
            while lLevel or rLevel:
                if rLevel and not mLevel:
                    turnRight(moveSpeed * speedFactor)
                    break
                elif lLevel and not mLevel:
                    turnLeft(moveSpeed * speedFactor * decayFactor)
                elif decayFactor <= 0.0:
                    break
                elif not mLevel and not lLevel and not rLevel:
                    moveBackward(0.2)
                else:
                    break
                decayFactor -= 0.1
                turnRight(moveSpeed*decayFactor)
                #time.sleep(0.1)
                lLevel = ReadChannel(lSensor) in range(800,1000)
                rLevel = ReadChannel(rSensor) in range(800,1000)
                mLevel = ReadChannel(mSensor) in range(800,1000)
                print("lL: " + str(ReadChannel(lSensor)), end = " ")
                print("mL: " + str(ReadChannel(mSensor)), end = " ")
                print("rL: " + str(ReadChannel(rSensor)))
                print("RIGHTL00P")
            print("right")
        elif not mLevel and not lLevel and not rLevel:
            print("forward no reading")
            moveForward(moveSpeed)
            dist += moveSpeed * 2 * math.pi * 3
            if dist >=  100:#19:
                stop()
        time.sleep(delay)
except KeyboardInterrupt:
    stop()
        
