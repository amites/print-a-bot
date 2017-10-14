from logging import getLogger
from os import path
from subprocess import call, check_output

from django.conf import settings


logger = getLogger(__name__)


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
