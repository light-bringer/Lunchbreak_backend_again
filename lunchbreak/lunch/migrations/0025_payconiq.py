# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-04-06 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0024_money_new_renamed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='online_payments_enabled',
            field=models.BooleanField(default=True, help_text='Online betalingen ingeschakeld, er moet een Payconiq merchant gelinkt worden voor online betalingen aanvaard kunnen worden.', verbose_name='online betalingen ingeschakeld'),
        ),
    ]
