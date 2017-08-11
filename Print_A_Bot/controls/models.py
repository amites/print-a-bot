# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class LightShow(models.Model):
	name = models.CharField(max_length=100)

class LightShowStep(models.Model):
	show = ForeignKey(LightShow)
	light = models.IntegerField(choices=settings.LED_CHOICES)
	red = models.IntegerField()
	green = models.IntegerField()
	blue = models.IntegerField()
	order = models.IntegerField()
