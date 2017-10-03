from logging import getLogger

from django import forms
from django.utils.translation import ugettext as _

try:
    from djconfig.forms import ConfigForm as Form
except ImportError:
    Form = forms.Form


logger = getLogger(__name__)


class WifiForm(Form):
    wifi_ssid = forms.CharField(label=_('Wifi Network SSID'), initial=None, required=False)
    wifi_password = forms.CharField(label=_('Wifi Network Password'), initial=None, required=False)
    wifi_encryption = forms.CharField(label=_('Wifi Network Encryption Type'), initial=None, required=False)