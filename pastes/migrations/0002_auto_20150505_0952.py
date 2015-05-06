# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paste',
            name='expiration_datetime',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
