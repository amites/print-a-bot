from django import forms
from django.utils.translation import ugettext as _
from djconfig.forms import ConfigForm


class WifiForm(ConfigForm):
    wifi_ssid = forms.CharField(label=_('Wifi Network SSID'), initial=None, required=False)
    wifi_password = forms.CharField(label=_('Wifi Network Password'), initial=None, required=False)
    wifi_encryption = forms.CharField(label=_('Wifi Network Encryption Type'), initial=None, required=False)