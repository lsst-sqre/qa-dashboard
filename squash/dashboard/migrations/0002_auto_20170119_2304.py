# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='measurement',
            name='data',
        ),
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
            field=jsonfield.fields.JSONField(help_text='Data blobs produced by the job.', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='metadata',
            field=jsonfield.fields.JSONField(help_text='Measurement metadata', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='operator',
            field=models.CharField(max_length=2, help_text='Operator used to test measurement value against metric specification', default='<'),
        ),
        migrations.AddField(
            model_name='metric',
            name='parameters',
            field=jsonfield.fields.JSONField(help_text='Parameters used to define the metric', default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='metric',
            name='reference',
            field=jsonfield.fields.JSONField(help_text='Metric reference', default=None),
        ),
        migrations.AddField(
            model_name='metric',
            name='specs',
            field=jsonfield.fields.JSONField(help_text='Array of metric specification', default=None),
        ),
        migrations.AddField(
            model_name='metric',
            name='unit',
            field=models.CharField(max_length=16, help_text='Metric unit, astropy compatible string', default='', null=True, blank=True),
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
            field=models.CharField(serialize=False, help_text='Metric name', max_length=16, primary_key=True),
        ),
    ]
