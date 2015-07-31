# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0009_auto_20150731_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paste',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='paste',
            name='updated',
            field=models.DateTimeField(auto_now=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pastereport',
            name='checked',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pasteversion',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
    ]
