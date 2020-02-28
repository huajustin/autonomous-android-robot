import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

col0 = 7
col1 = 20
col2 = 8
row0 = 21
row1 = 25
GPIO.setup(col0,GPIO.OUT)   #col0 7   
GPIO.setup(col2,GPIO.OUT)  #col2 8
GPIO.setup(col1,GPIO.OUT) #col1 20
GPIO.setup(row0,GPIO.IN,pull_up_down = GPIO.PUD_UP) #row0 21
GPIO.setup(row1,GPIO.IN,pull_up_down = GPIO.PUD_UP)   #row1 25

while True:
    GPIO.output(col0,GPIO.LOW)
    GPIO.output(col1,GPIO.HIGH)
    GPIO.output(col2,GPIO.HIGH)
    if GPIO.input(25) == 0:
        print("4")
    GPIO.output(col0,GPIO.HIGH)
    GPIO.output(col1,GPIO.LOW)
    GPIO.output(col2,GPIO.HIGH)
    if GPIO.input(25) == 0:
        print("5")
    elif GPIO.input(21) == 0:
        print("2")

    GPIO.output(col0,GPIO.HIGH)
    GPIO.output(col1,GPIO.HIGH)
    GPIO.output(col2,GPIO.LOW)
    if GPIO.input(25) == 0:
        print("6")
        
    time.sleep(0.2)

