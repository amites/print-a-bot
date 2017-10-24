# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views import View

from controls.forms import LightShowForm, LightShowStepForm
from controls.models import LightShow, LightShowStep
from controls.utils import light, motor
from controls.utils.system import call_sudo_command


def home(request):
    context = {
        'lightshows': LightShow.objects.all()
    }
    return render(request, 'home.html', context)


def single_lightshow(request, lightshow_id):
    try:
        lightshow = LightShow.objects.get(id=lightshow_id)
        call_sudo_command('system_config', new_process=True, lightshow=lightshow_id)
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
        cmd_str = request.GET.get('cmd', None)
        if cmd_str in ['forward', 'f']:
            cmd = motor.forward
        elif cmd_str in ['reverse', 'r']:
            cmd = motor.reverse
        elif cmd_str in ['left', ';']:
            cmd = motor.left
        elif cmd_str in ['right', 'r']:
            cmd = motor.right
        elif cmd_str in ['stop', 's']:
            cmd = motor.stop
        else:
            cmd = None

        if cmd:
            motor.setup()
            cmd()

        context = {
            'cmd_str': cmd_str,
        }
        return render(request, 'controls/motor_move.html', context)


class ShowLights(View):
    def get(self, request):
        show_num = request.GET.get('show', None)
        show_exists = LightShow.objects.filter(pk=show_num).exists()
        # light.set_light(obj.lightshowstep_set.values_list('hex_color', flat=True), 1)
        if show_exists:
            call_sudo_command('system_config', new_process=True, lightshow=show_num)

        context = {
            'light_shows': LightShow.objects.all(),
        }
        return render(request, 'controls/light.html', context)