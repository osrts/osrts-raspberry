#!/usr/bin/env python
# Program launched by program.py

from threading import Thread, Condition, Timer
import RPi.GPIO as GPIO
import time

class LedController:
    # Internal class that is a singleton
    class __OnlyOneModel:
        def __init__(self):
            pass
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(18,GPIO.OUT)
            GPIO.setup(23,GPIO.OUT)

    # The instance
    instance = None

    def __init__(self):
        if not LedController.instance:
            LedController.instance = LedController.__OnlyOneModel()

    def switch(self, pin, state):
        pass
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,state)

    def blink(self, pin):
        #print("Blink")
        GPIO.setup(pin, GPIO.OUT) #Setup GPIO Pin to OUT
        GPIO.output(pin,True) #Switch on pin
        time.sleep(1) #Wait
        GPIO.output(pin,False) #Switch off pin

    def fast_blink(self, pin):
        #print("Blink")
        GPIO.setup(pin, GPIO.OUT) #Setup GPIO Pin to OUT
        GPIO.output(pin,True) #Switch on pin
        time.sleep(0.5) #Wait
        GPIO.output(pin,False) #Switch off pin

    def start(self):
        pass
        GPIO.setup(18, GPIO.OUT) #Setup GPIO Pin to OUT
        GPIO.output(18,True) #Switch on
        GPIO.setup(23, GPIO.OUT) #Setup GPIO Pin to OUT
        GPIO.output(23,True) #Switch on pin
        time.sleep(3) #Wait
        GPIO.output(18,False) #Switch off pin
        GPIO.output(23,False) #Switch off pin

    def importConfig(self):
        for x in range(0, 10):
            GPIO.setup(18, GPIO.OUT) #Setup GPIO Pin to OUT
            GPIO.output(18,True) #Switch on
            GPIO.setup(23, GPIO.OUT) #Setup GPIO Pin to OUT
            GPIO.output(23,True) #Switch on pin
            time.sleep(0.300) #Wait
            GPIO.output(18,False) #Switch off pin
            GPIO.output(23,False) #Switch off pin
            time.sleep(0.300) #Wait
