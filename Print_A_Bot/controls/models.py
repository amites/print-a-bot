# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class LightShow(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class LightShowStep(models.Model):
    show = models.ForeignKey(LightShow)
    light = models.IntegerField(choices=settings.LED_CHOICES)
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order', ]
        unique_together = ('show', 'light', 'order')

    def __str__(self):
        return '{}, LED {}, order {}, color ({},{},{})'.format(self.show, self.light, self.order, self.red, self.green, self.blue)

    
