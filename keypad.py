import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(7,GPIO.OUT)   #col2 7   
GPIO.setup(8,GPIO.OUT)  #col0 8
GPIO.setup(25,GPIO.IN,pull_up_down = GPIO.PUD_UP)   #row1 25

while True:
    GPIO.output(7,GPIO.LOW)
    GPIO.output(8,GPIO.HIGH)
    if GPIO.input(25) == 0:
        print("4")
    GPIO.output(7,GPIO.HIGH)
    GPIO.output(8,GPIO.LOW)
    if GPIO.input(25) == 0:
        print("6")

    time.sleep(0.2)

