# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import redis
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views import View

from controls.forms import LightShowForm, LightShowStepForm
from controls.models import LightShow


def home(request):
    context = {
        'lightshows': LightShow.objects.all()
    }
    return render(request, 'home.html', context)


def single_lightshow(request, lightshow_id):
    try:
        lightshow = LightShow.objects.get(id=lightshow_id)
    except LightShow.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Light show with ID {} does not exist.'.format(lightshow_id))
        return redirect(reverse('home'))
    context = {
        'lightshow': lightshow
    }
    return render(request, 'single_lightshow.html', context)


class MovementView(View):
    def get(self, request):
        context = {}
        return render(request, 'move.html', context)

    def post(self, request):
        pass


class LightsView(View):
    def get(self, request):
        context = {}
        return render(request, 'lights.html', context)

    def post(self, request):
        pass


class NewLightShowView(View):
    def get(self, request):
        context = {
            'form': LightShowForm,
        }
        return render(request, 'create_lightshow.html', context)

    def post(self, request):
        form = LightShowForm(request.POST)

        # revert back to blank form if not valid
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, 'create_lightshow.html', context)
        form.save()
        return redirect(reverse('create_lightshow_step'))


class NewLightShowStepView(View):
    def get(self, request):
        context = {
            'form': LightShowStepForm
        }
        return render(request, 'create_lightshow_step.html', context)

    def post(self, request):
        form = LightShowStepForm(request.POST)
        # lightshow = LightShow.objects.get(id=lightshow_id)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'create_lightshow_step.html', context)
        # if request.POST.get('add_another'):
        #     form.save()
        #     return redirect(reverse('create_lightshow_step', kwargs={'lightshow_id': lightshow.id}))

        form.save()
        return redirect(reverse('home'))


class MoveBot(View):
    def get(self, request):
        cmd_str = request.GET.get('cmd', '').lower()
        r = redis.Redis()

        if cmd_str in ['forward', 'f']:
            r.publish('controls', 'forward')
        elif cmd_str in ['reverse', 'r']:
            r.publish('controls', 'reverse')
        elif cmd_str in ['left', 'l']:
            r.publish('controls', 'left')
        elif cmd_str in ['right', 'r']:
            r.publish('controls', 'right')
        elif cmd_str in ['stop', 's']:
            r.publish('controls', 'stop')
        else:
            cmd_str = 'None'

        context = {
            'cmd_str': cmd_str,
        }
        return render(request, 'controls/motor_move.html', context)
