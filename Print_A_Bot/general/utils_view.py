import json
import logging
import os

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.utils.encoding import smart_str


logger = logging.getLogger(__name__)


def return_accel_file(fpath, file_name=None):
    """
    Shortcut to return a file using web-server x-accel.
    Useful for securing access to a file while not locking a thread.

    :param fpath: Full path to file.
    :type fpath: str
    :param file_name: _optional_ file name to present to user will default to
                      fpath file name.
    :type file_name: str
    :returns: HttpResponse with X-Sendfile header for Apache or Nginx
    """
    if not os.path.exists(fpath):
        logger.warning('Attempt to download file %s which does not exist' % fpath)
        return Http404
    if not file_name:
        file_name = os.path.basename(fpath)

    response = HttpResponse(mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)

    if getattr(settings, 'WEBSERVER', 'APACHE') == 'NGINX':
        response['X-Accel-Redirect'] = fpath
    else:
        response['X-Sendfile'] = fpath
    response['Content-Length'] = os.stat(fpath).st_size
    logger.debug('sending file %s' % fpath)
    logger.debug('file name: %s' % file_name)
    return response


def return_json(data, **kwargs):
    """
    Quick shortcut to allow pretty printing JSON when debug is True.
    """
    if type(data) == dict:
        # ensure translation output is a string
        if data.get('msg', None) is not None:
            data['msg'] = unicode(data['msg'])
        if data.get('success', None) is not None:
            data['success'] = data.get('success', False)
    if settings.DEBUG:
        kwargs['indent'] = 4

    response = HttpResponse(json.dumps(data, **kwargs), content_type='application/json')

    if settings.DEBUG:
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
    return response


def return_success_msg(request, msg, response, success=True, extra_fields=None, **kwargs):
    """
    Return a success or fail message appropriate for ajax or standard call.

    :param HttpRequest request: request from view
    :param str msg: Rendered msg to be passed to notify_data or added as a django message.
    :param HttpResponse response: Response if request made without ajax.
    :param bool success: Whether to return success or error message.
    :param extra_fields: Extra json fields to return.
    :return: HttpResponse based on request.is_ajax
    """
    if request.is_ajax():
        data = {
            'success': success,
            'msg': unicode(msg),
        }
        if extra_fields:
            data.update(extra_fields)
        return return_json(data)
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    if type(response) == str:
        response = render(request, response, kwargs.get('context', {}))
    return response


def return_default_msg(request, msg, response=None, success=True, extra_fields=None, **kwargs):
    if response is None:
        response = redirect(reverse(settings.GENERAL_DEFAULT_REVERSE))
    return return_success_msg(request, msg, response, success, extra_fields, **kwargs)
