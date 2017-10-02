"""
Basic utilities to control 2 servo motors using the TB6612FNG control board.
"""

import RPi.GPIO as GPIO


def setup():
    """
    Run before calling any of the direction methods below.
    Assumes that all PINS are defined in settings and 
        that GPIO.setmode has been called.
    """
    if settings.PIN_MODE == 'board':
        GPIO.setmode(GPIO.BOARD)
    elif settings.PIN_MODE == 'bcm':
        GPIO.setmode(GPIO.BCM)
    else:
        raise ValueError('PIN_MODE must be one of:  bpard, bdm')

    GPIO.setup(settings.AIN1, GPIO.OUT)
    GPIO.setup(settings.AIN2, GPIO.OUT)
    GPIO.setup(settings.BIN1, GPIO.OUT)
    GPIO.setup(settings.BIN2, GPIO.OUT)
    GPIO.setup(settings.STBY, GPIO.OUT)
    GPIO.setup(settings.PWMA, GPIO.OUT)
    GPIO.setup(settings.PWMB, GPIO.OUT)


def forward():
    GPIO.output(settings.AIN1, GPIO.HIGH)
    GPIO.output(settings.AIN2, GPIO.LOW)
    GPIO.output(settings.BIN1, GPIO.HIGH)
    GPIO.output(settings.BIN2, GPIO.LOW)
    GPIO.output(settings.STBY, GPIO.HIGH)
    GPIO.output(settings.PWMA, GPIO.HIGH)
    GPIO.output(settings.PWMB, GPIO.HIGH)


def reverse():
    GPIO.output(settings.AIN1, GPIO.LOW)
    GPIO.output(settings.AIN2, GPIO.HIGH)
    GPIO.output(settings.BIN1, GPIO.LOW)
    GPIO.output(settings.BIN2, GPIO.HIGH)
    GPIO.output(settings.STBY, GPIO.HIGH)
    GPIO.output(settings.PWMA, GPIO.HIGH)
    GPIO.output(settings.PWMB, GPIO.HIGH)


def left():
    GPIO.output(settings.AIN1, GPIO.HIGH)
    GPIO.output(settings.AIN2, GPIO.LOW)
    GPIO.output(settings.BIN1, GPIO.LOW)
    GPIO.output(settings.BIN2, GPIO.HIGH)
    GPIO.output(settings.STBY, GPIO.HIGH)
    GPIO.output(settings.PWMA, GPIO.HIGH)
    GPIO.output(settings.PWMB, GPIO.HIGH)


def right():
    GPIO.output(settings.AIN1, GPIO.LOW)
    GPIO.output(settings.AIN2, GPIO.HIGH)
    GPIO.output(settings.BIN1, GPIO.HIGH)
    GPIO.output(settings.BIN2, GPIO.LOW)
    GPIO.output(settings.STBY, GPIO.HIGH)
    GPIO.output(settings.PWMA, GPIO.HIGH)
    GPIO.output(settings.PWMB, GPIO.HIGH)


def stop():
    GPIO.output(settings.AIN1, GPIO.LOW)
    GPIO.output(settings.AIN2, GPIO.LOW)
    GPIO.output(settings.BIN1, GPIO.LOW)
    GPIO.output(settings.BIN2, GPIO.LOW)
    GPIO.output(settings.STBY, GPIO.LOW)
    GPIO.output(settings.PWMA, GPIO.LOW)
    GPIO.output(settings.PWMB, GPIO.LOW)
