# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pastes', '0002_paste_encrypted'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasteReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=32)),
                ('text', models.TextField()),
                ('checked', models.BooleanField(default=False)),
                ('paste', models.ForeignKey(to='pastes.Paste')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='paste',
            name='deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='paste',
            name='removal_reason',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='paste',
            name='removed',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
