# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-31 16:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lightshowstep',
            options={'ordering': ['order']},
        ),
        migrations.AlterUniqueTogether(
            name='lightshowstep',
            unique_together=set([('light', 'order')]),
        ),
    ]
