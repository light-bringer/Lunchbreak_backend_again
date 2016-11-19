# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-13 20:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0013_roundingdecimalfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientgroup',
            name='calculation',
            field=models.PositiveIntegerField(choices=[(0, 'Altijd de groepsprijs'), (1, 'Duurder bij toevoegen, zelfde bij aftrekken'), (2, 'Duurder bij toevoegen, goedkoper bij aftrekken')], default=2, help_text='Manier waarop de prijs moet berekened worden indien ingrediënten aangepast toegevoegd of afgetrokken worden.', verbose_name='prijsberekening'),
        ),
    ]