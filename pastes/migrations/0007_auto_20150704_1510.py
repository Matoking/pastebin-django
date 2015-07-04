# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0006_paste_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='paste',
            name='size',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pasteversion',
            name='size',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
