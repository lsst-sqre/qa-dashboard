# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='ci_name',
            field=models.CharField(max_length=32, help_text='Name of the Jenkins project,                                e.g. validate_drp'),
        ),
    ]
