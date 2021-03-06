# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-11 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LightShow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LightShowStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('light', models.IntegerField(choices=[(1, b'LED 1'), (2, b'LED 2')])),
                ('red', models.IntegerField()),
                ('green', models.IntegerField()),
                ('blue', models.IntegerField()),
                ('order', models.IntegerField()),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='controls.LightShow')),
            ],
        ),
    ]
