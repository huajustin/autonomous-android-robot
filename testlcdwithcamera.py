import digitalio
import board
from picamera import PiCamera
from time import sleep
from PIL import Image, ImageDraw

import adafruit_rgb_display.st7735 as st7735        # pylint: disable=unused-import

 
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
while(True):

    camera.capture('/home/pi/Desktop/picture 1.bmp')
    image = Image.open("picture 1.bmp")
 
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
    
