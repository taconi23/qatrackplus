# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-10 17:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0004_auto_20171222_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='date_acceptance',
            field=models.DateField(help_text='Changing acceptance date will delete unit available times that occur before it'),
        ),
        migrations.AlterField(
            model_name='unitavailabletime',
            name='date_changed',
            field=models.DateField(blank=True, help_text='Date the units available time changed or will change'),
        ),
    ]