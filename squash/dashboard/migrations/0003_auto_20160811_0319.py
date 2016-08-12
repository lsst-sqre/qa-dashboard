# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20160811_0047'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='ci_dataset',
            field=models.CharField(help_text='Name of the dataset, e.g cfht', default='cfht', max_length=16),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='job',
            name='ci_label',
            field=models.CharField(help_text='Name of the platform, eg. centos-7', default='centos-7', max_length=16),
            preserve_default=False,
        ),
    ]
