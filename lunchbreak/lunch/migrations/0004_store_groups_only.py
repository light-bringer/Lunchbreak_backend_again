# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-26 20:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0003_auto_20170825_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='groups_only',
            field=models.BooleanField(default=False, help_text='Enkel leden van de groepen van deze winkel kunnen bij deze winkel bestellen.', verbose_name='enkel groepen'),
        ),
    ]
