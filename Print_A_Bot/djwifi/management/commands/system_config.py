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
from djconfig.models import Config

from djwifi.forms import WifiForm


logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # linux config
        parser.add_argument('--timezone', action='store_true', dest='set_timezone', default=False,
                            help=_('Set system timezone from config.')),
        parser.add_argument('--cleanup', action='store_true', dest='cleanup', default=False,
                            help=_('Clean up system to maintain stability.')),
        parser.add_argument('--shutdown', action='store_true', dest='shutdown', default=False,
                            help=_('Run shutdown scripts.'))

        # wifi
        parser.add_argument('--ap_on', action='store_true', dest='ap_on', default=False,
                            help=_('Start wireless access point.')),
        parser.add_argument('--ap_off', action='store_true', dest='ap_off', default=False,
                            help=_('Stop wireless access point.')),
        parser.add_argument('--set_wifi', action='store_true', dest='set_wifi', default=False),

    def __init__(self):
        self.dev = False
        
        self.wifi_ssid = None
        self.wifi_password = None
        self.wifi_encryption = None
        
        super(Command, self).__init__()

    # server config #

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

    # wifi #

    def _configure_wifi(self):
        try:
            self.wifi_ssid = Config.objects.get(key='wifi_ssid').value.replace('+', ' ')
            self.wifi_password = Config.objects.get(key='wifi_password').value
            self.wifi_encryption = Config.objects.get(key='wifi_encryption').value
        except Config.DoesNotExist as e:
            raise ValueError('Config key {} does not exist'.format(e.message))

    def _set_wifi_network(self):
        if not self.wifi_ssid:
            logger.warning('wifi_ssid not configured, aborting network config.')
            return

        wpa_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'

        encryption = self.wifi_encryption

        with open(wpa_conf_path, 'r') as f:
            wpa_data = f.read()

        if re.search(self.wifi_ssid, wpa_data):
            logger.info('SSID {} already configured'.format(self.wifi_ssid))
            return

        wpa_priorities = re.findall('priority=(\d+)', wpa_data)
        wpa_priorities.sort()

        wifi_data = {
            'ssid': '"{}"'.format(self.wifi_ssid),
            'priority': int(wpa_priorities[-1]) + 1,
        }

        if 'wpa' in encryption:
            wpa_out = check_output(['wpa_passphrase', self.wifi_ssid, self.wifi_password])
            wifi_data['psk'] = re.search('\tpsk=(.*)', wpa_out).group(1)

            wpa_entry = '''network={{
    ssid={ssid}
    psk={psk}

    proto=RSN
    key_mgmt=WPA-PSK
    pairwise=CCMP
    auth_alg=OPEN
    priority={priority}
}}'''
        else:
            wpa_entry = '''network={{
    ssid={ssid}
    key_mgmt=NONE
    priority={priority}
}}'''

        with open(wpa_conf_path, 'a') as f:
            f.write('\n\n')
            f.write(wpa_entry.format(**wifi_data))

        if not settings.DEBUG:
            call(['shutdown', '-r', 'now'])

    @staticmethod
    def _cycle_wifi(mode=None):
        call(['ifdown', settings.WIFI_INTERFACE])
        if mode is not None:
            call(['iwconfig', settings.WIFI_INTERFACE, 'mode', mode])
        call(['ifup', settings.WIFI_INTERFACE])

    # wifi access point #

    @staticmethod
    def _setup_wifi_ap():
        try:
            check_output(['ifconfig', settings.WIFI_AP_NAME])
            logger.info('wifi vap %s already setup' % settings.WIFI_AP_NAME)
            return True
        except CalledProcessError:
            logger.info('Setting up virtual access point interface')
        output = check_output(['ifconfig', settings.WIFI_INTERFACE])
        logger.debug('ifconfig %s outout:\n%s' % (settings.WIFI_INTERFACE, output))
        # set MAC address for wap0 virtual device
        result = re.search(r'HWaddr (.*)', output)
        if not result:
            logger.warning('Unable to find MAC address for %s skipping virtual device config' % settings.WIFI_INTERFACE)
            return
        grps = result.group(1).strip().split(':')
        hex_char = 'A' if grps[0][1] != 'A' else '6'
        grps[0] = grps[0][0] + hex_char
        fake_mac = ':'.join(grps)
        # logger.debug('creating wap0 virtual device:\n\t%s' % ' '.join(['iw', 'phy', settings.WIFI_PHY_INTERFACE,
        #                                                                'interface', 'add', settings.WIFI_AP_NAME,
        #                                                                'type', '__ap']))
        call(['iw', 'phy', settings.WIFI_PHY_INTERFACE, 'interface', 'add', settings.WIFI_AP_NAME, 'type', '__ap'])
        logger.debug('added %s virtual device on phy %s' % (settings.WIFI_INTERFACE, settings.WIFI_PHY_INTERFACE))
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

    def handle(self, *args, **options):
        print 'running handle'

        logger.info('Running system_config with options:\n\t%s' % str(options))

        self.dev = options.get('dev', False)

        if options.get('cleanup'):
            self._clean_logs()

        if options.get('set_wifi', False):
            self._configure_wifi()
            self._set_wifi_network()

        # configure access point
        if options.get('ap_on', False):
            self._ap_start()

        if options.get('ap_off', False):
            self._ap_stop()

        if options.get('shutdown', False):
            # self._set_pins(False)
            self._clean_logs()
