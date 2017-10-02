# Raspberry Pi Config
PIN_MODE = 'board'
# PIN_MODE = 'bcm'

# Set which GPIO pins the drive outputs are connected
PWMA = 22
AIN1 = 13
AIN2 = 15
PWMB = 12
BIN1 = 16
BIN2 = 18
STBY = 7


# RPi LED control
# LED A and B are pin numbers..
LED_A = 5
LED_B = 10
LED_CHOICES = (
    (1, 'LED 1'),
    (2, 'LED 2'),
)


try:
    from local_config import *
except ImportError:
    pass
