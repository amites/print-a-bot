import time

from colour import Color
from django.conf import settings
import RPi.GPIO as GPIO


def _setup_light():
    if settings.PIN_MODE == 'board':
        GPIO.setmode(GPIO.BOARD)
    else:
        GPIO.setmode(GPIO.BCM)
    for led_num, led_data in settings.LED_CHOICES:
        for pin_num in led_data.values():
            GPIO.setup(pin_num, GPIO.OUT)


def set_light(values, led_num):
    _setup_light()

    led_data = dict(settings.LED_CHOICES).get(led_num)
    pins = {
        'r': GPIO.PWM(led_data['r'], settings.LED_FREQ),
        'g': GPIO.PWM(led_data['g'], settings.LED_FREQ),
        'b': GPIO.PWM(led_data['b'], settings.LED_FREQ),
    }
    pins['r'].start(1)
    pins['g'].start(1)
    pins['b'].start(1)

    for n, value in enumerate(values):
        color = Color(value)
        pins['r'].ChangeDutyCycle(color.red * 100)
        pins['g'].ChangeDutyCycle(color.green * 100)
        pins['b'].ChangeDutyCycle(color.blue * 100)

        if len(values) <= n+1:
            break

        for new_color in color.range_to(values[n+1], 50):
            pins['r'].ChangeDutyCycle(new_color.red * 100)
            pins['g'].ChangeDutyCycle(new_color.green * 100)
            pins['b'].ChangeDutyCycle(new_color.blue * 100)
            time.sleep(.05)
