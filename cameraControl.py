import RPi.GPIO as GPIO
import os
import time
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
import digitalio
import board
from picamera import PiCamera
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735 
#import motorFunctions

#region setup
#############################################
# pins variables setup
#############################################
#setup http server
host_name = '137.82.226.228'    #Raspberry Pi IP address
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
camera.resolution = (640, 480) 
width = disp.width   # we swap height/width to rotate it to landscape!
height = disp.height
image = Image.new('RGB', (width, height))
camera.framerate = 30


# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)


#endregion

#region classes
#############################################
# class set up
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
                camera.stop_preview()
                continue
            #capture the picture and save it to the desktop
            else:
                camera.start_preview()
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
                Camera control: <br />
                <input type="submit" name="submit" value="Camera"> 
            </form>
            <img src="picture1.bmp" width="640" height="480">
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
        if post_data=="Camera":
            #when the user press on the camera button, 
            #change the state of camera state to start/stop taking pictures
            if not cThread.is_alive():
                cThread.start()
            else:
                c.changeState()
            
        self._redirect('/')    # finished handling request, redirect back to the root url
#endregion

#############################################
# main function
#############################################
# setup the server
http_server = HTTPServer((host_name, host_port), MyServer)
print("server open")
try:
    #handle request until the user exit the web
    http_server.serve_forever()
except KeyboardInterrupt:
    print("server exception")
    http_server.server_close()