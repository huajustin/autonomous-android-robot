import sys
import os
import time
import math
import spidev
import bluetooth
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from adafruit_motorkit import MotorKit
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
                <input type="submit" name="submit" value="Backward"><br />
                <input type="submit" name="submit" value="Stop"> 
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
        moveSpeed = 0.35
        if post_data == 'Forward':
            moveForward(moveSpeed)
            print("car is moving forward")
        elif post_data == 'Backward':
            moveBackward(moveSpeed)
            print("car is moving backward")
        if post_data =='Left':
            turnLeft(moveSpeed)
            print("car is rotating left")
        elif post_data == 'Right':
            turnRight(moveSpeed)
            print("car is rotating right")
        if post_data == 'Stop':
            stop()
            print("stopped")
        
        self._redirect('/') # finished handling request, redirect back to the root url

#############################################
# Main loop function
#############################################
# this is for reading parameters given by the command line execution
control_mode = sys.argv[1]

#default move speed for all three modes
moveSpeed = 0.35

if control_mode == "1":
    print("bluetooth mode")
    # bluetooth control
    # get server socket and set UUID and port number
    server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    uuid = "56e8a14a-80b3-11e5-8bcf-feff819cdc9f"
    port = bluetooth.PORT_ANY

    # set up the server socket and listen in on the connection
    server_socket.bind(("",port))
    server_socket.listen(1)
    bluetooth.advertise_service( server_socket, "Bluetooth Server",
                                service_id = uuid, 
                    service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],profiles = [ bluetooth.SERIAL_PORT_PROFILE ]
                    )
    print("Currently looking for connections...")

    # blocking call, waits until a client connects to the socket
    client_socket,address = server_socket.accept()
    print("Accepted connection from {}".format(address))

    # loop to receive communication from client
    while 1: 
        data = client_socket.recv(1024)
        print(data)
        # if client sends an exit signal, then break this loop
        if (data == b'\x00'):
            break
        # if client unexpectedly disconnects, also break
        if not data:
            break
        if data == b'\x01':
            stop()
        if data == b'\x02':
            moveForward(moveSpeed)
        if data == b'\x03':
            moveBackward(moveSpeed)
        if data == b'\x04':
            turnLeft(0.3)
        if data == b'\x05':
            turnRight(0.3)
        if data == b'\x06':
            rotateLeftInPlace()
        if data == b'\x07':
            rotateRightInPlace()

    # close sockets
    print("Client disconnected. Now quitting...")
    client_socket.close()
    server_socket.close()

elif control_mode == "2":
    print("web server mode")
    #use the webserver

    # setup the server
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("server open")
    try:
        #handle request until the user exit the web
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("server exception")
        http_server.server_close()

else:
    print("default mode")
    dist = 0
    speedFactor = 0.5
    UPPER = 1000
    LOWER = 500
    delay = 0.03

    #pid control variables 
#     KP = 0.245
#     KD = 0.018
    KP=0.248
    KD = 0.02
    error2 = 0.8
    prev_error = 0.0
    min_speed = 0
    max_speed = 1
    direction = 0
    try:
        while True:
            lLevel = ReadChannel(lSensor) in range(LOWER,UPPER)
            mLevel = ReadChannel(mSensor) in range(LOWER,UPPER)
            rLevel = ReadChannel(rSensor) in range(LOWER,UPPER)
            
            print("l: " + str(ReadChannel(lSensor)), end = " ")
            print("m: " + str(ReadChannel(mSensor)), end = " ")
            print("r: " + str(ReadChannel(rSensor)))
            if mLevel:
                #as long as the middle level is detecting, go straight
                dist = 0
                moveForward(moveSpeed)
                direction = 0
            elif mLevel and not lLevel and not rLevel:
                dist = 0
                moveForward(moveSpeed)
                print("forward")
                prev_error = 0.0
                direction = 0
            elif mLevel and lLevel and rLevel:
                dist = 0
                moveForward(moveSpeed)
                print("90cross")
                prev_error = 0.0
                direction = 0
            elif (mLevel and lLevel and not rLevel) or lLevel or direction == 1:
                dist = 0
                #turnLeft(0.3)
                #use the pid control to turn left
                LEFT_MOTOR.throttle = -max(min(moveSpeed - (error2 * KP + prev_error * KD),max_speed),min_speed)
                RIGHT_MOTOR.throttle = max(min(moveSpeed + (error2 * KP + prev_error * KD),max_speed),min_speed)
                prev_error = (error2 * KP + prev_error * KD)/KP
                print("left, l: " + str(LEFT_MOTOR.throttle)+" r: "+str(RIGHT_MOTOR.throttle))
                direction = 1
            elif (mLevel and not lLevel and rLevel) or rLevel or direction == 2:
                dist = 0
                #turnRight(0.3)
                #use pid control to turn right
                LEFT_MOTOR.throttle = max(min(moveSpeed + (error2 * KP + prev_error * KD),max_speed),min_speed)
                RIGHT_MOTOR.throttle = -max(min(moveSpeed - (error2 * KP + prev_error * KD),max_speed),min_speed)
                prev_error = (error2 * KP + prev_error * KD)/KP
                print("right, l: " + str(LEFT_MOTOR.throttle)+" r: "+str(RIGHT_MOTOR.throttle))
                direction = 2
            else:
                print("forward no reading")
                direction = 0
                moveForward(moveSpeed)
                dist += moveSpeed * 2 * math.pi * 3
                if dist >=  30: # 30 for 3cm
                    stop()
            time.sleep(delay)
    except KeyboardInterrupt:
        stop()
        
