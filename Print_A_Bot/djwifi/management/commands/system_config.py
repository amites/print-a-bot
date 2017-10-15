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

    #################
    # System Config #
    #################

    @staticmethod
    def _write_system_template(file_path, template, context=None):
        if path.exists(file_path):
            # backup old file
            rename(file_path, '%s--%s' % (file_path, datetime.now().strftime('%Y-%m-%d--%H-%M')))
        with open(file_path, 'w+') as f:
            f.write(render_to_string('system/{}'.format(template), context if context else {}))

    def _get_ap_context(self, hostname=None):
        if hostname is None:
            hostname = getattr(settings, 'HOST_NAME', settings.PROJECT_NAME)

        return {
            'hostname': str(hostname),
            'ssid': str(hostname),
            'password': settings.WIFI_PASSWORD,
        }

    def _set_hostname(self, hostname=None):
        context = self._get_ap_context()

        logger.info('setting hostname to {hostname}'.format(**context))

        # hosts
        self._write_system_template('/etc/hosts', 'hosts', context)

        # hostname
        hostname_path = '/etc/hostname'
        call(['rm', hostname_path])
        with open(hostname_path, 'w+') as f:
            f.write(context['hostname'])
        call(['hostname', context['hostname']])

        call(['service', 'avahi-daemon', 'restart'])

        # hostapd
        self._write_system_template('/etc/hostapd/hostapd.conf', 'access_point/hostapd.conf', context)

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

    def _setup_wifi_ap(self):
        try:
            check_output(['ifconfig', settings.WIFI_AP_NAME])
            logger.info('wifi ap %s already setup' % settings.WIFI_AP_NAME)
            return True
        except CalledProcessError:
            logger.info('Setting up virtual access point interface')
        call(['service', 'hostapd', 'stop'])
        call(['service', 'dnsmasq', 'stop'])
        context = self._get_ap_context()

        self._write_system_template('/etc/dnsmasq.conf', 'access_point/dnsmasq.conf')
        self._write_system_template('/etc/hostapd/hostapd.conf', 'access_point/hostapd.conf', context)
        self._write_system_template('/etc/network/interfaces', 'access_point/interfaces', context)
        self._write_system_template('/etc/default/hostapd', 'access_point/default_hostapd', context)
        self._write_system_template('/etc/dhcpcd.conf', 'access_point/dhcpcd.conf', context)
        
        call(['systemctl', 'enable', 'hostapd', ])
        call(['systemctl', 'enable', 'dnsmasq', ])
        return True

    def _ap_start(self):
        logger.info('Starting access point')
        self._setup_wifi_ap()

        call(['service', 'hostapd', 'start'])
        call(['service', 'dnsmasq', 'start'])

        logger.info('Access point started')

    def _disable_wifi_ap(self):
        call(['systemctl', 'disable', 'hostapd', ])
        call(['systemctl', 'disable', 'dnsmasq', ])

        context = self._get_ap_context()
        self._write_system_template('/etc/network/interfaces', 'interfaces', context)
        self._write_system_template('/etc/dhcpcd.conf', 'dhcpcd.conf', context)

    def _ap_stop(self):
        logger.info('Stopping access point')
        call(['service', 'hostapd', 'stop'])
        call(['service', 'dnsmasq', 'stop'])

        self._disable_wifi_ap()

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
