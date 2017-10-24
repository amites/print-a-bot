# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from controls.models import LightShow, LightShowStep


# https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#inlinemodeladmin-objects
class LightShowStepInline(admin.TabularInline):
    model = LightShowStep


class LightShowAdmin(admin.ModelAdmin):
    inlines = [
        LightShowStepInline,
    ]


admin.site.register(LightShow, LightShowAdmin)
admin.site.register(LightShowStep)
