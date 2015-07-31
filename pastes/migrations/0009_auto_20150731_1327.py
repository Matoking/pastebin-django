# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0008_pasteversion_encrypted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paste',
            name='char_id',
            field=models.CharField(max_length=8, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastecontent',
            name='hash',
            field=models.CharField(max_length=64, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pasteversion',
            name='encrypted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
