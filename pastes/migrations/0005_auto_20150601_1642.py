# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0004_auto_20150601_1634'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paste',
            old_name='current_version',
            new_name='version',
        ),
    ]
