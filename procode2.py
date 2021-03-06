import RPi.GPIO as gpio
import cv2
import numpy as np
from picamera import PiCamera
import time
from picamera.array import PiRGBArray
gpio.setmode(gpio.BOARD)
rmotor1 = 7
rmotor2 = 11
lmotor2 = 13
lmotor1 = 15
gpio.setup(rmotor1,gpio.OUT)
gpio.setup(rmotor2,gpio.OUT)
gpio.setup(lmotor1,gpio.OUT)
gpio.setup(lmotor2,gpio.OUT)
pwmr1 = gpio.PWM(rmotor1,100)
pwmr2 = gpio.PWM(rmotor2,100)
pwml1 = gpio.PWM(lmotor1,100)
pwml2 = gpio.PWM(lmotor2,100)
pwmr1.start(0)
pwmr2.start(0)
pwml1.start(0)
pwml2.start(0)
def forward():
    pwmr2.ChangeDutyCycle(75)
    pwmr1.start(0)
    pwml2.ChangeDutyCycle(75)
    pwml1.start(0)
    time.sleep(.08)
def right():
    pwmr1.start(0)
    pwmr2.ChangeDutyCycle(75)
    pwml1.ChangeDutyCycle(75)
    pwml2.start(0)
    time.sleep(.08)
def left():
    pwmr1.ChangeDutyCycle(75)
    pwmr2.start(0)
    pwml1.start(0)
    pwml2.ChangeDutyCycle(75)
    time.sleep(.08)
def stop():
    gpio.output(rmotor1,gpio.HIGH)
    gpio.output(rmotor2,gpio.HIGH)
    gpio.output(lmotor1,gpio.HIGH)
    gpio.output(lmotor2,gpio.HIGH)
kern_dilate = np.ones((8,8),np.uint8)
kern_erode = np.ones((3,3),np.uint8)
camera = PiCamera()
camera.resolution = (320,240)
camera.framerate = 30
rawCapture = PiRGBArray(camera,size=(320,240))
time.sleep(0.001)
for frame in camera.capture_continuous(rawCapture,format = 'bgr',use_video_port = True):
    image = frame.array
    grey = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    fill = cv2.GaussianBlur(grey,(5,5),0)
    ret, mask = cv2.threshold(fill,35,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    ret, mask1 = cv2.threshold(mask,122,255,cv2.THRESH_BINARY_INV)
    mask2 = cv2.erode(mask1,kern_erode)
    mask3 = cv2.dilate(mask2,kern_dilate)
    _, contours, _ = cv2.findContours(mask3,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        if cnt is not None:
            area = cv2.contourArea(cnt)
            #print area
            if(area>=25000):
                cv2.drawContours(image,cnt,-1,(255,0,0),3)
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #print "cx = ",cx
                #print "cy = ",cy
                if(130<=cx<=180):
                    print ("straight")
                    forward()
                elif(cx>=181):
                    print ("right")
                    right()
                elif(cx<=129):
                    print ("left")
                    left()
                else:
                    print ('stop')
                    stop()
    cv2.imshow('test',mask3)
    cv2.imshow('test1',image)
    rawCapture.truncate(0)
    if(cv2.waitKey(1)&0xFF==ord(' ')):
        break
gpio.cleanup()
