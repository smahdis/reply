# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-29 18:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0009_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='vote_type',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]