#!/usr/bin/python

import re
import sys
from os import path
from subprocess import call, check_output


CODE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
PROJECT_DIR = path.join(CODE_DIR, 'Print_A_Bot')
MANAGE_PATH = path.join(PROJECT_DIR, 'manage.py')


def main():
    out = check_output(['iwconfig', ])
    if not out.count('ESSID'):
        # append Print_A_Bot path to python path to import modules
        sys.path.append(PROJECT_DIR)
        from Print_A_Bot import settings
        from djwifi.iw_parse import call_iwlist

        # check access points in range
        iw_data = call_iwlist(settings.WIFI_INTERFACE)
        wpa_conf_path = '/etc/wpa_supplicant/wpa_supplicant.conf'
        with open(wpa_conf_path) as f:
            wpa_data = f.read()

        # if there's a known access point stop
        for ssid in re.findall('ssid="?(.*?)"?\n', wpa_data):
            if iw_data.count(ssid):
                return

        # no known access point kick on access point mode
        call(['python', MANAGE_PATH, 'system_config', '--ap_on'])


if __name__ == '__main__':
    main()
