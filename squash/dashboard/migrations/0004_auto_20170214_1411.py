# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20160811_0319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersession',
            name='user',
        ),
        migrations.AddField(
            model_name='measurement',
            name='data',
            field=jsonfield.fields.JSONField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='ci_name',
            field=models.CharField(max_length=32, help_text='Name of the Jenkins project,e.g. validate_drp'),
        ),
        migrations.AlterField(
            model_name='metric',
            name='units',
            field=models.CharField(max_length=16, blank=True),
        ),
        migrations.DeleteModel(
            name='UserSession',
        ),
    ]
