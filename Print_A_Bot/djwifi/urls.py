from django.conf.urls import patterns, url

from djconfig.registry import register
from djwifi.forms import WifiForm
from operations.forms import SettingForm


urlpatterns = patterns(
    'djwifi.views',

    url(r'^wifi_connect', 'wifi_connect', name='connect'),

    url(r'^list$', 'wifi_list', name='list'),
    url(r'^current$', 'wifi_current', name='current'),
    url(r'^disconnect$', 'wifi_disconnect', name='disconnect'),

    url(r'^access_point', 'access_point', name='access_point'),

    url(r'^$', 'wifi_home', name='home'),

    # temporary alias
    url(r'^config$', 'wifi_connect', name='config'),
    url(r'^scan$', 'wifi_list', name='scan'),
)


# TODO: port config form to use app registry -- https://github.com/nitely/django-djconfig
register(SettingForm)
register(WifiForm)