import time
from logging import getLogger
from os import path, remove

from django.conf import settings
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

    # lights #
    @staticmethod
    def _run_light(lightshow_id):
        light_file_path = path.join(settings.BASE_DIR, 'light_running')
        if path.exists(light_file_path):
            while True:
                time.sleep(1)
                if not path.exists(light_file_path):
                    break
        with open(light_file_path, 'w+') as f:
            f.write('running')
        try:
            obj = LightShow.objects.get(pk=lightshow_id)
        except LightShow.DoesNotExist:
            logger.error('LightShow with id {} does not exist'.format(lightshow_id))
            return
        logger.info('Running LightShow {}'.format(lightshow_id))
        set_light(obj.lightshowstep_set.values_list('hex_color', flat=True), 1)
        remove(light_file_path)

    def handle(self, *args, **options):
        if options.get('lightshow', False):
            self._run_light(options['lightshow'])
