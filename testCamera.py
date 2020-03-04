from picamera import PiCamera
from time import sleep
camera =PiCamera()
camera.annotate_text = "Hello world!"
camera.annotate_text_size = 100
camera.awb_mode = 'sunlight'
camera.start_preview()
camera.start_recording('/home/pi/Desktop/video.h264')
for effect in camera.IMAGE_EFFECTS:
    camera.image_effect = effect
    camera.annotate_text = "Effect: %s" % effect
    sleep(5)
camera.stop_recording()
camera.stop_preview()
#for i in range(0,5):
    #sleep(1)
    #camera.capture('/home/pi/Desktop/picture %d.jpg'%i)
#camera.stop_preview()