import RPi.GPIO as GPIO
import os
import time
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
import digitalio
import board
from picamera import PiCamera
from PIL import Image, ImageDraw
import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import
#import motorFunctions


host_name = '137.82.226.228'    # Change this to Raspberry Pi IP address
host_port = 8000

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()
camera =PiCamera()
camera.resolution = (128, 128) 

disp = st7735.ST7735R(spi, rotation=270, height=128, x_offset=2, y_offset=3,  

                    cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)

width = disp.width   # we swap height/width to rotate it to landscape!
height = disp.height
image = Image.new('RGB', (width, height))
camera.framerate = 30

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

class MyCamera():
    def __init__(self):
        self.running = True

    def terminate(self):
        self.running = False
    
    def run(self):
        while True:
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

c = MyCamera()
cThread = Thread(target = c.run)

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
        #generate the html web with four buttons to control the robot to move forward, backward, left and right
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
            #motorFunctions.moveForward(speed)
            print("car is moving forward")
        elif post_data == 'Backward':
            #motorFunctions.moveBackward(speed)
            print("car is moving backward")
        if post_data =='Left':
            #motorFunctions.turnLeft(speed)
            print("car is rotating left")
        elif post_data == 'Right':
            #motorFunctions.turnRight(speed)
            print("car is rotating right")
        
        if post_data=="Camera":
            if not cThread.is_alive():
                cThread.start()

        self._redirect('/')    # finished handling request, redirect back to the root url

# setup the server
http_server = HTTPServer((host_name, host_port), MyServer)
print("server open")
try:
    #handle request until the controller exit the web
    http_server.serve_forever()
except KeyboardInterrupt:
    print("server exception")
    http_server.server_close()
    c.terminate()