import re
from logging import getLogger
from subprocess import call, check_output

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from djwifi.forms import WifiForm
from djwifi.iw_parse import call_iwlist, get_djwifi_list
from general.utils_view import return_success_msg
from controls.utils.system import call_sudo_command


logger = getLogger(__name__)


def wifi_home(request):
    context = {
        'configured': settings.WIFI_INTERFACE,
    }
    return render(request, 'djwifi/configure.html', context)


@api_view(['GET', ])
def wifi_list(request):
    logger.debug('settings.WIFI_INTERFACE: %s' % settings.WIFI_INTERFACE)
    iw_data = call_iwlist(settings.WIFI_INTERFACE)
    if not iw_data:
        return Response({'success': False,
                         'msg': _('Wireless is busy, please try again shortly.')})
    wifi_data = get_djwifi_list(iw_data.split('\n'))
    logger.debug('wifi data:\n\t%s' % str(wifi_data))
    return Response({
        'access_points': wifi_data,
        'success': True,
    })


@api_view(['GET', ])
def wifi_current(request):
    if not settings.WIFI_INTERFACE:
        return Response({'success': False})
    output_ifconfig = check_output(['ifconfig', settings.WIFI_INTERFACE])
    result = re.search(r'inet ([\d\.]+)', output_ifconfig)  # only supports ipv4
    if result:
        ip = result.group(1)
        output_iwconfig = check_output(['iwconfig', settings.WIFI_INTERFACE])
        result = re.search(r'ESSID:(.*)', output_iwconfig)
        if result:
            essid = result.group(1).strip().replace('"', '')
        else:
            essid = ''

        quality = None
        result = re.search(r'Link Quality=(\d+)/(\d+) ', output_iwconfig)
        if result:
            try:
                quality = int(float(float(result.group(1)) / float(result.group(2))) * 100)
            except ValueError:
                logger.warning('Unable to parse Signal Quality from iwconfig')
        if quality is None:
            result = re.search(r'Signal level=(.*?) ', output_iwconfig)
            if result:
                try:
                    quality = 2 * (int(result.group(1)) + 100)
                except ValueError:
                    logger.warning('Unable to parse Signal Level from iwconfig')
        return Response({
            'ip': ip,
            'essid': essid,
            'quality': quality,
            'success': True,
        })
    return Response({'success': False})


def wifi_connect(request):
    if request.method == 'POST':
        form = WifiForm(request.POST)
        if form.is_valid():
            form.save()
            logger.debug('wifi_connect: %s' % str(form.cleaned_data))
            call_sudo_command('system_config', new_process=True, set_wifi=True, reboot=True)
            return return_success_msg(request, _('Connecting to %s, system will reboot.' %
                                                 form.cleaned_data['wifi_ssid']), redirect(reverse('wifi:home')))
    return return_success_msg(request, _('No wifi specified, aborting.'), redirect(reverse('wifi:home')), False)


def wifi_disconnect(request):
    call(['ifconfig', settings.WIFI_INTERFACE, 'down'])
    # overwrite network interfaces?
    # call_sudo_command('system_config', )
    return return_success_msg(request, _('Print-a-Bot will disconnect from the network momentarily.'
                                         'You should be able to connect to it as an access point shortly.'),
                              redirect(reverse('wifi:home')), kwargs={'new_url': 'http://%s' % settings.WIFI_AP_IP})


def access_point(request):
    """
    Turn on access point mode.
    """
    call_sudo_command('system_config', new_process=True, ap_on=True, reboot=True)
    return return_success_msg(request, _('Garden Genie is being switched to access point mode.'),
                              redirect(reverse('home')))
