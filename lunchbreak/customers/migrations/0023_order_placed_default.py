# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-04-01 13:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0022_group_payment_online_only'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='placed',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Tijdstip waarop de bestelling werd geplaatst.', verbose_name='tijd van plaatsing'),
        ),
    ]
