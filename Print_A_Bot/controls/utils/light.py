import time

from colour import Color
from django.conf import settings
import RPi.GPIO as GPIO


def _setup_light():
    GPIO.setmode(settings.PIN_MODE)
    for led_num, led_data in settings.LED_CHOICES:
        for pin_num in led_data.keys():
            GPIO.setup(pin_num, GPIO.OUT)


def set_light(values, led_num):
    pins = {}
    led_data = dict(settings.LED_CHOICES).get(led_num)
    pins[led_num] = {
        'r': GPIO.PWM(led_data['r'], settings.LED_FREQ),
        'g': GPIO.PWM(led_data['g'], settings.LED_FREQ),
        'b': GPIO.PWM(led_data['b'], settings.LED_FREQ),
    }
    pins['r'].start(1)
    pins['g'].start(1)
    pins['b'].start(1)

    for n, value in enumerate(values):
        color = Color(value)
        pins[led_num]['r'].ChangeDutyCycle(color.red * 100)
        pins[led_num]['g'].ChangeDutyCycle(color.green * 100)
        pins[led_num]['b'].ChangeDutyCycle(color.blue * 100)

        for new_color in color.range_to(values[n+1], 50):
            pins[led_num]['r'].ChangeDutyCycle(new_color.red * 100)
            pins[led_num]['g'].ChangeDutyCycle(new_color.green * 100)
            pins[led_num]['b'].ChangeDutyCycle(new_color.blue * 100)
            time.sleep(.05)
