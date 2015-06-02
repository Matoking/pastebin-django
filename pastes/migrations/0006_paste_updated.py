# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0005_auto_20150601_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='paste',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 1, 17, 17, 54, 386976, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
