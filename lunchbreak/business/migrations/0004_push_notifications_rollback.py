# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-26 13:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_push_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeetoken',
            name='service',
            field=models.IntegerField(choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')], default=2, verbose_name='Notification service'),
        ),
        migrations.AlterField(
            model_name='stafftoken',
            name='service',
            field=models.IntegerField(choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive')], default=2, verbose_name='Notification service'),
        ),
    ]
