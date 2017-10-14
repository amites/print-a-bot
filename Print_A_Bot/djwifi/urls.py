from django.conf.urls import url

from djwifi.views import access_point, wifi_connect, wifi_current, wifi_disconnect, wifi_home, wifi_list 

urlpatterns = (
    url(r'^wifi_connect', wifi_connect, name='connect'),

    url(r'^list$', wifi_list, name='list'),
    url(r'^current$', wifi_current, name='current'),
    url(r'^disconnect$', wifi_disconnect, name='disconnect'),

    url(r'^access_point', access_point, name='access_point'),

    url(r'^$', wifi_home, name='home'),

    # temporary alias
    url(r'^config$', wifi_connect, name='config'),
    url(r'^scan$', wifi_list, name='scan'),
)
