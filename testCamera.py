from picamera import PiCamera
from time import sleep
camera =PiCamera()
camera.start_preview()
for i in range(0,5):
    sleep(1)
    camera.capture('/home/pi/Desktop/picture %d.jpg'%i)
camera.stop_preview()