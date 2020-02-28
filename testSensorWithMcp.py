import spidev
import time
import os
import RPi.GPIO as GPIO

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
GPIO.setmode(GPIO.BCM)  
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 

# Define sensor channels
channel = 0

 
# Define delay between readings
delay = 0.1
 
while True:
 
  level = ReadChannel(channel)
 

  # Print out results
  if level in range(980,1000):
      print(level)
      print("inline")
  else:
      print("DJJ")
  # Wait before repeating loop
  time.sleep(delay)