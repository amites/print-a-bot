import tempfile
import time
from logging import getLogger
from os import path, remove

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from controls.models import LightShow
from controls.utils.light import set_light


logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # lights
        parser.add_argument('--lightshow', dest='lightshow',
                            help=_('Run lightshow for given id'))
        parser.add_argument('--light', dest='light',
                            help=_('Which LED_PIN to use'))

    def __init__(self, *args, **kwargs):
        self.light_file_path = path.join(tempfile.tempdir, 'light_running')
        super(Command, self).__init__(*args, **kwargs)

    @staticmethod
    def _start_run_file(file_path):
        if path.exists(file_path):
            while True:
                time.sleep(1)
                if not path.exists(file_path):
                    break
        with open(file_path, 'w+') as f:
            f.write('True')

    @staticmethod
    def _clean_running_path(file_path):
        if path.exists(file_path):
            remove(file_path)

    # lights #
    def _run_light(self, lightshow_id, led_pin=1):
        self._start_running_path(self.light_file_path)
        try:
            obj = LightShow.objects.get(pk=lightshow_id)
        except LightShow.DoesNotExist:
            logger.error('LightShow with id {} does not exist'.format(lightshow_id))
            return
        logger.info('Running LightShow {}'.format(lightshow_id))
        set_light(obj.lightshowstep_set.values_list('hex_color', flat=True), led_pin)
        remove(self.light_file_path)

    def handle(self, *args, **options):
        if options.get('lightshow', False):
            try:
                self._run_light(options['lightshow'], options.get('light', 1))
            finally:
                self._clean_running_path(self.light_file_path)
