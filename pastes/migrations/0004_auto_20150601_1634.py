# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pastes', '0003_auto_20150525_1612'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasteVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.IntegerField()),
                ('note', models.CharField(default=b'', max_length=1024)),
                ('title', models.CharField(max_length=128)),
                ('hash', models.CharField(max_length=64)),
                ('format', models.CharField(max_length=64)),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('paste', models.ForeignKey(to='pastes.Paste')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='paste',
            name='current_version',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
