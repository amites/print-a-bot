# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View



def home(request):
	context = {}
	return render(request, 'home.html', context)


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


def creat_lightshow(request):
	pass


