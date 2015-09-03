# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0021_service_inactive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='confirmedTotal',
            field=models.DecimalField(default=None, null=True, max_digits=7, decimal_places=2, blank=True),
        ),
    ]
