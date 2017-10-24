# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class LightShow(models.Model):
    name = models.CharField(max_length=100)
    light = models.IntegerField(choices=settings.LED_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.name

class LightShowStep(models.Model):
    show = models.ForeignKey(LightShow, related_name='step')
    light = models.IntegerField(choices=settings.LED_CHOICES)
    red = models.IntegerField(null=True, blank=True)
    green = models.IntegerField(null=True, blank=True)
    blue = models.IntegerField(null=True, blank=True)
    hex_color = models.CharField(null=True, blank=True, max_length=7)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order', ]
        unique_together = ('show', 'light', 'order')

    def __str__(self):
        return '{}, LED {}, order {}, color ({},{},{})'.format(self.show, self.light, self.order, self.red, self.green, self.blue)
