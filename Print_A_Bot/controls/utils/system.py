import subprocess
from logging import getLogger
from os import path, setpgrp

from django.conf import settings


logger = getLogger(__name__)


def call_sudo_command(command, new_process=False, **kwargs):
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
    cmd = ['sudo', 'python', path.join(settings.BASE_DIR, 'manage.py'), command] + cmd_args
    if new_process:
        subprocess.Popen(['nohup', ] + cmd,
                         stdout=open('/dev/null', 'w'),
                         stderr=open('/var/log/print-a-bot.log', 'a+'),
                         preexec_fn=setpgrp)
    else:
        subprocess.call(cmd)


def process_running(name):
    """
    Check if a process with the given name is running.
    """
    output = subprocess.check_output(['ps', 'aux', '--cols', '200'])  # prevent ps from trimming columns
    if not output.count(name):
        logger.debug('No process named %s' % name)
        return
    for line in output.split('\n'):
        if line.count(name):
            return True
    return False
