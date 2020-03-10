import os
import time
import math
import spidev
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from adafruit_motorkit import MotorKit
from picamera import PiCamera

import digitalio
import board
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735 

#server modules import
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
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
    LEFT_MOTOR.throttle = speed
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

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

#############################################
# Web server definitions and functions
#############################################

#setup http server
host_name = '137.82.226.231'    #Raspberry Pi IP address
host_port = 8000

#setup LCD
# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,  
                    cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)

#setup camera
camera =PiCamera()
camera.resolution = (128, 128) 
width = disp.width   # we swap height/width to rotate it to landscape!
height = disp.height
image = Image.new('RGB', (width, height))
camera.framerate = 30

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

#############################################
# camera class set up
#############################################
class MyCamera():
    #class for camera multi-threading
    #so that the camera can take pictures constantly while the user is controlling the robot on the webpage
    def __init__(self):
        self.running = True

    def changeState(self):
        #change the state of running
        #if running == true, the while loop in the run() function will take pictures
        #if running == false, the while loop will not take pictures simply idle
        self.running = not self.running
    
    def run(self):
        while True:
            if not self.running:
                continue
            #capture the picture and save it to the desktop
            camera.capture('/home/pi/Desktop/picture1.bmp')
            image = Image.open("picture1.bmp")

            # Scale the image to the smaller screen dimension
            image_ratio = image.width / image.height
            screen_ratio = width / height
            if screen_ratio < image_ratio:
                scaled_width = image.width * height // image.height
                scaled_height = height
            else:
                scaled_width = width
                scaled_height = image.height * width // image.width
                image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

            # Crop and center the image
                x = scaled_width // 2 - width // 2
                y = scaled_height // 2 - height // 2
            image = image.crop((x, y, x + width, y + height))

            # Display image.
            disp.image(image)

#set up camera and its thread for control in the MyServer class
c = MyCamera()
cThread = Thread(target = c.run)

#############################################
# server class set up
#############################################
class MyServer(BaseHTTPRequestHandler):
    #this is the class that sets up the website and handle requests sent by the user
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
        #generate the html web with six buttons 
        # first four buttons are used to control the robot to move forward, backward, left and right
        #fifth button is used to stop the robot
        #last button is used to control the camera to start/stop taking pictures
        html = '''
            <html>
            <body style="width:960px; margin: 20px auto;" >
            
            <h1>CPEN291 Project 1 Raspberry Pi web robot control</h1>
            <p>Current temperature is {}</p>
            
            <form action="/" method="POST">
                Robot control: <br />
                <input type="submit" name="submit" value="Forward"> <br />
                <input type="submit" name="submit" value="Left">
                <input type="submit" name="submit" value="Right"><br />
                <input type="submit" name="submit" value="Backward"><br />
                <input type="submit" name="submit" value="Stop"><br />
                <input type="submit" name="submit" value="Camera"> 
            </form>
            </body>
            </html>
        '''
        #the following code is used to show the current CPU temperature of raspberry pi
        #and make sure that the website can be properly shown
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))


    def do_POST(self):
        #we get the request from the user
        #call the specific function in motor functions to handle the request
        content_length = int(self.headers['Content-Length'])    # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")   # Get the data
        post_data = post_data.split("=")[1]    # Only keep the value
        print(post_data)
        speed = 1
        if post_data == 'Forward':
            motorFunctions.moveForward(speed)
            print("car is moving forward")
        elif post_data == 'Backward':
            motorFunctions.moveBackward(speed)
            print("car is moving backward")
        if post_data =='Left':
            motorFunctions.turnLeft(speed)
            print("car is rotating left")
        elif post_data == 'Right':
            motorFunctions.turnRight(speed)
            print("car is rotating right")
        
        if post_data == 'Stop':
            motorFunctions.stop()
            print("stopped")
        if post_data=="Camera":
            #when the user press on the camera button, 
            #change the state of camera state to start/stop taking pictures
            if not cThread.is_alive():
                cThread.start()
            else:
                c.changeState()
            
        self._redirect('/')    # finished handling request, redirect back to the root url

#############################################
# Main loop function
#############################################
server_enabled = False
if server_enabled:
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("server open")
    try:
        #handle request until the user exit the web
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("server exception")
        http_server.server_close()
else:
    dist = 0
    speedFactor = 0.5
    moveSpeed = 0.35
    direction = 0 # left is 1, right is 2
    UPPER = 1000
    LOWER = 800
    delay = 0.2

    try:
        while True:
            lLevel = ReadChannel(lSensor) in range(LOWER,UPPER)
            mLevel = ReadChannel(mSensor) in range(LOWER,UPPER)
            rLevel = ReadChannel(rSensor) in range(LOWER,UPPER)
            
            print("l: " + str(ReadChannel(lSensor)), end = " ")
            print("m: " + str(ReadChannel(mSensor)), end = " ")
            print("r: " + str(ReadChannel(rSensor)))
            if mLevel:
                dist = 0
                moveForward(moveSpeed)
                direction = 0
                
            elif mLevel and not lLevel and not rLevel:
                dist = 0
                moveForward(moveSpeed)
                direction = 0
                print("forward")
            elif mLevel and lLevel and rLevel:
                dist = 0
                moveForward(moveSpeed)
                direction = 0
                print("90cross")
            elif (mLevel and lLevel and not rLevel) or lLevel:
                dist = 0
                decayFactor = 0.5
                turnLeft(0.3)
                direction = 1
                print("left")
            elif (mLevel and not lLevel and rLevel) or rLevel:
                dist = 0
                decayFactor = 0.5
                turnRight(0.3)
                direction = 2
                print("right")
            else:
                print("forward no reading")
                moveForward(moveSpeed)
                dist += moveSpeed * 2 * math.pi * 3
                if dist >=  30: # 30 for 3cm
                    stop()
            time.sleep(delay)
    except KeyboardInterrupt:
        stop()
            
