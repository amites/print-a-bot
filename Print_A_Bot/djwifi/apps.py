from django.apps import AppConfig


class DjWifiConfig(AppConfig):
    name = 'djwifi'
    verbose_name = "Django Wifi"

    def ready(self):
        self.register_config()

    @staticmethod
    def register_config():
        import djconfig
        from .forms import WifiForm

        djconfig.register(WifiForm)
