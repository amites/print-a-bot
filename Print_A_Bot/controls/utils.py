import re
from logging import getLogger
from os import path
from subprocess import call, check_output

from django.conf import settings


logger = getLogger('gg')


def get_gpio_from_pin(pin):
    """
    Dumb parser from pin string to a gpio number.

    :param pin: P#_## style pin string
    :return: gpio # from settings.GPIO_MAP
    """
    try:
        pin_set, pin_num = pin.split('_')
    except ValueError:
        return False
    try:
        return settings.GPIO_MAP[pin_set.upper()][int(pin_num)]
    except KeyError:
        return False


def get_gpio_status(gpio):
    """
    Get current pin state for given gpio pin.

    :param gpio: gpio pin
    :return: True if Out, False if In, else None
    """
    if not gpio:
        logger.warning('invalid gpio value -- %s' % gpio)
        return None
    with open('/sys/class/gpio/gpio%s/direction' % gpio, 'r') as f:
        status = f.read()
    if status == 'out':
        return True
    elif status == 'in':
        return False
    return None


def get_pin_status(status):
    logger.debug('raw status: %s' % status)
    if type(status) == bool:
        status = 'out' if status else 'in'
    elif status not in ['in', 'out']:
        status = {'on': 'out', 'off': 'in'}.get(status, None)
    logger.debug('return status: %s' % status)
    return status
    

def switch_device(pin, status='off'):
    """
    Turn a relay pin on or off.
    :param pin: P#_## style pin string or gpio #
    :param status: str or boolean whether to turn status or off
    :return: True status success, else False
    """
    logger.debug('called switch_device with arguments\n\tpin: %s\n\tstatus: %s' % (pin, status))
    if pin.count('_'):
        pin = get_gpio_from_pin(pin)

    state = get_pin_status(status)

    logger.debug('pin: %s -- state: %s' % (pin, state))

    if get_gpio_status(pin) == status:
        return None

    # TODO: update to use `unexport` to turn "off" vs `direction` = "in"

    if pin and state:
        logger.debug('switch_device pin: %s -- state: %s' % (pin, state))
        call(['sudo', 'python', path.join(settings.DIRNAME, 'cmds', 'switch_gpio.py'), str(pin), state])
        # TODO: save value for pin switch to model
        return True
    return False


def call_sudo_command(command, **kwargs):
    """
    Call django management command with kwargs -- kwargs keys must match command line option names vs var names.
    """
    cmd_args = []
    for k, v in kwargs.iteritems():
        if type(v) is bool:
            cmd_args.append('--%s' % k)
        else:
            cmd_args.append('--{}={}'.format(k, v))
    logger.debug('making sudo command call %s %s' % (command, ' '.join(cmd_args)))
    call(['sudo', 'python', path.join(settings.DIRNAME, 'manage.py'), command] + cmd_args)


def process_running(name):
    output = check_output(['ps', 'aux', '--cols', '200'])  # prevent ps from trimming columns
    if not output.count(name):
        logger.debug('No process named %s' % name)
        return
    for line in output.split('\n'):
        if line.count(name):
            return True
    return False


def get_uuid():
    content = check_output('blkid')
    result = re.search(r'UUID="(.*?)"', content)
    if result:
        return result.group(1)
    return None


def shorten_values(data):
    result = []
    for row in data:
        obj = {}
        for key, val in dict(row).iteritems():
            obj[key.split('__')[-1]] = val
        result.append(obj)
    return result
