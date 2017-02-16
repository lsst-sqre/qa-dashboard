# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20160811_0319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='metric',
            name='condition',
        ),
        migrations.RemoveField(
            model_name='metric',
            name='design',
        ),
        migrations.RemoveField(
            model_name='metric',
            name='minimum',
        ),
        migrations.RemoveField(
            model_name='metric',
            name='stretch',
        ),
        migrations.RemoveField(
            model_name='metric',
            name='units',
        ),
        migrations.RemoveField(
            model_name='metric',
            name='user',
        ),
        migrations.AddField(
            model_name='job',
            name='blobs',
            field=json_field.fields.JSONField(help_text='Data blobs produced by the job.', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='metadata',
            field=json_field.fields.JSONField(help_text='Measurement metadata', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='operator',
            field=models.CharField(help_text='Operator used to test measurementvalue against metric specification', max_length=2, default='<'),
        ),
        migrations.AddField(
            model_name='metric',
            name='parameters',
            field=json_field.fields.JSONField(help_text='Parameters used to define the metric', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='reference',
            field=json_field.fields.JSONField(help_text='Metric reference', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='specs',
            field=json_field.fields.JSONField(help_text='Array of metric specification', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='unit',
            field=models.CharField(help_text='Metric unit, astropy compatible string', max_length=16, default='', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='ci_name',
            field=models.CharField(help_text='Name of the Jenkins project,e.g. validate_drp', max_length=32),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='value',
            field=models.FloatField(help_text='Metric scalar measurement'),
        ),
        migrations.AlterField(
            model_name='metric',
            name='description',
            field=models.TextField(help_text='Metric description'),
        ),
        migrations.AlterField(
            model_name='metric',
            name='metric',
            field=models.CharField(help_text='Metric name', max_length=16, primary_key=True, serialize=False),
        ),
    ]
