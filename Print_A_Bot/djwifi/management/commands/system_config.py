import re
from datetime import datetime
from logging import getLogger
from os import path, remove, rename, system
from subprocess import call, check_output, CalledProcessError
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from djconfig import config

logger = getLogger(__name__)

LOG_NAMES = [
    # 'gardengenie.log',
    # 'apache-access.log',
    # 'apache-access.log',
]

# SRC_PATH = path.abspath(path.join(path.dirname(settings.BASE_DIR), 'src'))
# SYSTEM_PATH = path.join(settings.BASE_DIR, 'system')
# CONFIG_PATH = path.join(SYSTEM_PATH, 'config')

WIFI_PACKAGE = 'compat'


class Command(BaseCommand):
    # TODO: add command line args to initial_config for individual functions
    def add_arguments(self, parser):
        # linux config
        parser.add_argument('--initial', '--full', action='store_true', dest='run_config', default=False,
                            help=_('Run a full initial configuration')),
        parser.add_argument('--dev', action='store_true', dest='dev', default=False,
                            help=_('Configure as a development hub.')),
        parser.add_argument('--install', action='store_true', dest='install_packages', default=False,
                            help=_('Whether to run package installation scripts.')),

        parser.add_argument('--host', action='store_true', dest='update_host', default=False,
                            help=_('Update system hostname using settings.HOST_NAME.')),
        parser.add_argument('--ntp', action='store_true', dest='configure_ntp', default=False,
                            help=_('Whether to configure and restart ntp service.')),
        parser.add_argument('--timezone', action='store_true', dest='set_timezone', default=False,
                            help=_('Set system timezone from config.')),
        parser.add_argument('--cleanup', action='store_true', dest='cleanup', default=False,
                            help=_('Clean up system to maintain stability.')),

        parser.add_argument('--startup', action='store_true', dest='startup', default=False,
                            help=_('Run startup actions')),

        # wifi
        parser.add_argument('--ap_on', action='store_true', dest='ap_on', default=False,
                            help=_('Start wireless access point.')),
        parser.add_argument('--ap_off', action='store_true', dest='ap_off', default=False,
                            help=_('Stop wireless access point.')),
        parser.add_argument('--set_wifi', action='store_true', dest='set_wifi', default=False),

        # beaglebone specific
        parser.add_argument('--no-heartbeat', action='store_true', dest='disable_heartbeat', default=False,
                            help=_('Whether to disable the Beaglebone Black led heartbeat.')),
        parser.add_argument('--pins-on', action='store_true', dest='pins_on', default=False,
                            help=_('Turn all GPIO pins on.')),
        parser.add_argument('--pins-off', action='store_true', dest='pins_off', default=False,
                            help=_('Turn all GPIO pins off.')),
        parser.add_argument('--shutdown', action='store_true', dest='shutdown', default=False,
                            help=_('Run shutdown scripts.'))

    def __init__(self):
        self.dev = False
        self.no_wifi = False
        self.run_config = False
        self.version = 0.00
        super(Command, self).__init__()

    # user management #

    @staticmethod
    def _add_user_group(username=None, user_group=None):
        if username is None:
            username = settings.PROJECT_NAME
        if user_group is None:
            user_group = settings.USER_GROUP
        logger.debug('adding user %s to group %s' % (username, user_group))
        call(['addgroup', username, user_group])

    # server config #

    @staticmethod
    def _configure_ntp(host=None):
        """
        Setup automated remote time sync.
        """
        logger.debug('running configure_ntp')
        if host is None:
            host = 'time.nist.gov'
        call(['service', 'ntp', 'stop'])
        call(['ntpdate', '-s', host])
        call(['service', 'ntp', 'start'])

    # package management apt-get / dpkg #

    def _install_packages(self):
        self._apt_install()
        self._apt_upgrade()
        self._fix_dpkg()

    @staticmethod
    def _apt_upgrade():
        logger.debug('running apt_upgrade')
        call(['apt-get', 'update'])
        call(['apt-get', 'upgrade', '-y'])

    def _apt_install(self):
        logger.debug('running apt_install')
        programs = settings.APT_GET_PROGRAMS
        if self.dev:
            programs += settings.APT_GET_DEV
        call(['apt-get', 'install', '-y'] + programs)

    @staticmethod
    def _fix_dpkg():
        logger.info('running fix_dpkg')
        call(['dpkg', '--configure', '-a'])

    @staticmethod
    def _kill_process(name):
        output = check_output(['ps', 'aux', '--cols', '200'])  # prevent ps from trimming columns
        if not output.count(name):
            logger.debug('No process named %s' % name)
            return
        for line in output.split('\n'):
            if line.count(name):
                result = re.search(r'\w+ +(\d+)', line)  # username   PID
                if result:
                    call(['kill', result.group(1)])
                    logger.info('killed process %s - %s' % (name, result.group(1)))
                else:
                    logger.info('found process %s but cannot find PID\n\t%s' % (name, line))

    @staticmethod
    def _write_system_template(file_path, template, context):
        if path.exists(file_path):
            # backup old file
            rename(file_path, '%s--%s' % (file_path, datetime.now().strftime('%Y-%m-%d--%H-%M')))
        with open(file_path, 'w+') as f:
            f.write(render_to_string('system/%s' % template, context))

    # wifi #

    @staticmethod
    def _set_wifi_interface():
        try:
            output = check_output('iwconfig')
        except OSError:
            logger.warning('iwlist not available -- could not set wifi_interface')
            return
        result = re.search('wlan\d', output)
        if not result:
            logger.warning('no wifi interface found -- could not set wifi_interface')
            return
        # config_save('wifi_interface', result.group(0))
        return True

    def _set_wifi_network(self):
        if not config.wifi_ssid:
            logger.warning('Wifi ssid not configured, aborting network config.')
            return

        encryption = config.wifi_encryption
        if 'wpa' in encryption:
            encryption = 'wpa'
        elif 'wep' in encryption:
            encryption = 'wep'
        else:
            encryption = False

        context = {
            'wifi_encryption': encryption,
            'wifi_password': config.wifi_password,
            'wifi_ssid': config.wifi_ssid,
            'wifi_interface': config.wifi_interface,
        }

        self._write_system_template('/etc/network/interfaces', 'interfaces', context)
        if not settings.DEBUG:
            call(['shutdown', '-r', 'now'])

    @staticmethod
    def _cycle_wifi(mode=None):
        call(['ifdown', config.wifi_interface])
        if mode is not None:
            call(['iwconfig', config.wifi_interface, 'mode', mode])
        call(['ifup', config.wifi_interface])

    # wifi access point #

    @staticmethod
    def _setup_wifi_vap():
        try:
            check_output(['ifconfig', settings.WIFI_AP_NAME])
            logger.info('wifi vap %s already setup' % settings.WIFI_AP_NAME)
            return True
        except CalledProcessError:
            logger.info('Setting up virtual access point interface')
        output = check_output(['ifconfig', config.wifi_interface])
        logger.debug('ifconfig %s outout:\n%s' % (config.wifi_interface, output))
        # set MAC address for wap0 virtual device
        result = re.search(r'HWaddr (.*)', output)
        if not result:
            logger.warning('Unable to find MAC address for %s skipping virtual device config' % config.wifi_interface)
            return
        grps = result.group(1).strip().split(':')
        hex_char = 'A' if grps[0][1] != 'A' else '6'
        grps[0] = grps[0][0] + hex_char
        fake_mac = ':'.join(grps)
        # logger.debug('creating wap0 virtual device:\n\t%s' % ' '.join(['iw', 'phy', settings.WIFI_PHY_INTERFACE,
        #                                                                'interface', 'add', settings.WIFI_AP_NAME,
        #                                                                'type', '__ap']))
        call(['iw', 'phy', settings.WIFI_PHY_INTERFACE, 'interface', 'add', settings.WIFI_AP_NAME, 'type', '__ap'])
        logger.debug('added %s virtual device on phy %s' % (config.wifi_interface, settings.WIFI_PHY_INTERFACE))
        call(['ifconfig', settings.WIFI_AP_NAME, 'hw', 'ether', fake_mac])
        logger.debug('set wap0 HW address to %s' % fake_mac)
        call(['ifconfig', settings.WIFI_AP_NAME, settings.WIFI_AP_IP, 'netmask', '255.255.255.0'])
        logger.debug('setup wap0 to ip %s' % settings.WIFI_AP_IP)
        logger.info('wifi vap %s setup' % settings.WIFI_AP_NAME)
        return True

    def _ap_start(self):
        logger.info('Starting access point')
        self._setup_wifi_vap()

        call(['ifconfig', settings.WIFI_AP_NAME, settings.WIFI_AP_IP, 'up'])
        logger.debug('brought up wap0 interface')
        # service fails silent with debian 1.0 hostapd package
        # call(['service', 'hostapd', 'restart'])
        self._kill_process('hostapd')
        call(['hostapd', '-B', '/etc/hostapd/hostapd.conf'])
        sleep(2)  # allow hostapd to start first
        call(['service', 'dnsmasq', 'restart'])
        logger.info('Access point started')

    def _ap_stop(self):
        logger.info('Stopping access point')
        # service calls don't always stop
        call(['service', 'dnsmasq', 'stop'])
        call(['service', 'hostapd', 'stop'])
        sleep(1)
        self._kill_process('dnsmasq')
        self._kill_process('hostapd')
        try:
            call(['iw', 'dev', settings.WIFI_AP_NAME, 'del'])
        except CalledProcessError:
            logger.info('%s not currently available' % settings.WIFI_AP_NAME)
        logger.info('access point stopped')

    # linux system #

    @staticmethod
    def _clean_logs(size=None):
        """
        !!!FARKING HACK!!! Clear all logs to prevent log files from filling up system.

        # proper would be dumping these to a remote system
        """
        if size is None:
            size = '100k'

        for log_path in settings.SYSTEM_LOG_PATHS:
            out = check_output(['find', log_path, '-type', 'f', '-name', '*.gz'])
            for file_path in out.splitlines():
                if path.exists(file_path):
                    logger.info('removing file %s' % file_path)
                    remove(file_path)

            out = check_output(['find', log_path, '-type', 'f', '-size', '+%s' % size])
            for file_path in out.splitlines():
                if path.exists(file_path):
                    logger.info('zeroing out file: %s' % file_path)
                    system('> %s' % file_path)

    # beaglebone black #

    @staticmethod
    def _disable_usr_led(usr_led=0):
        system('echo none > /sys/class/leds/beaglebone\:green\:usr%s/trigger' % usr_led)

    @staticmethod
    def __config_dev():

        settings_path = path.join(settings.PROJECT_PATH, settings.PROJECT_NAME, 'local_settings.py')
        system('printf "from dev_settings import *\nDEBUG=True" > %s' % settings_path)
        call(['chown', '%s:%s' % (settings.PROJECT_NAME, settings.USER_GROUP), settings_path])
        # call_command('loaddata', 'operations/fixtures/dev_pins.json')

    def handle(self, *args, **options):
        print 'running handle'

        logger.info('Running system_config with options:\n\t%s' % str(options))

        # register_config(SettingForm)
        # register_config(WifiForm)

        self.dev = options.get('dev', False)
        self.no_wifi = options.get('no_wifi', False)

        if options.get('run_config', False):
            try:
                self.version = float(config.version_unit)
            except TypeError:
                self.version = 0.00
            # self.__config_0_01()
            # self.__config_0_02()
            if self.dev:
                self.__config_dev()

        if options.get('cleanup'):
            self._clean_logs()
            self._configure_ntp()

        if options.get('install_packages', False):
            self._install_packages()

        if options.get('disable_heartbeat', False):
            self._disable_usr_led(usr_led=0)

        if options.get('configure_ntp', False):
            self._configure_ntp()

        # if options.get('update_host', False):
        #     self.configure_host()

        # if options.get('set_timezone', False):
        #     self.set_timezone()

        # configure GPIO Pins
        # if options.get('pins_on', False):
        #     self._set_pins(True)
        # if options.get('pins_off', False):
        #     self._set_pins(False)

        if options.get('set_wifi', False):
            self._set_wifi_network()
        # configure access point
        if options.get('ap_on', False):
            self._ap_start()

        if options.get('ap_off', False):
            self._ap_stop()

        if options.get('shutdown', False):
            # self._set_pins(False)
            self._clean_logs()
