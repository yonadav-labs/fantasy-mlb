# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2021-08-30 19:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='slate',
            name='date',
            field=models.DateField(default=datetime.date(2021, 8, 30)),
            preserve_default=False,
        ),
    ]
