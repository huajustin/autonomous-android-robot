import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(27,GPIO.IN)     
GPIO.setup(4,GPIO.IN)
GPIO.setup(22,GPIO.IN)
GPIO.setup(17,GPIO.IN)

while True:
    if (GPIO.input(27) == 0):
        time.sleep(0.01)
        print("RIGHT")
    if (GPIO.input(4) == 1):
        time.sleep(0.01)
        print("LEFT")
    if (GPIO.input(22) == 0):
        time.sleep(0.01)
        print("UP")
    if (GPIO.input(17) == 1):
        time.sleep(0.01)
        print("DOWN")