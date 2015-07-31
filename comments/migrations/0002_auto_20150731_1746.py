# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='edited',
            field=models.DateTimeField(auto_now=True, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='comment',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
            preserve_default=True,
        ),
    ]
