# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from django.views import View
from controls.forms import LightShowForm, LightShowStepForm
from controls.models import LightShow, LightShowStep



def home(request):
	context = {
		'lightshows': LightShow.objects.all()
	}
	return render(request, 'home.html', context)


def single_lightshow(request, lightshow_id):
	lightshow = LightShow.objects.get(id=lightshow_id)
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
                'form': LightShowForm,
            }
            return render(request, 'create_lightshow.html', context)
        form.save()
        return redirect(reverse('home'))


class NewLightShowStepView(View):
	def get(self, request):
		context = {
			'form': LightShowStepForm
		}
		return render(request, 'create_lightshow_step.html', context)

	def post(self, request):
		form = LightShowStepForm(request.POST)
		if not form.is_valid():
			context = {
				'form': LightShowStepForm
			}
			return render(request, 'create_lightshow_step.html', context)
		form.save()
		return redirect(reverse('home'))




