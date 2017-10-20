import json
import logging

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render


logger = logging.getLogger(__name__)


def return_json(data, **kwargs):
    """
    This should be replaced by Django REST API Return
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
