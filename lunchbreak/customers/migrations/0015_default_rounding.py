# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-02 13:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0014_roundingdecimalfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='description',
            field=models.TextField(blank=True, help_text='Bv: extra extra mayonaise graag!', verbose_name='opmerking bij de bestelling'),
        ),
    ]
