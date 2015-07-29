# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0007_auto_20150704_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='pasteversion',
            name='encrypted',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
