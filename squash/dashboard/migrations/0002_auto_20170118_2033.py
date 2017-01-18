# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='metric',
            old_name='condition',
            new_name='operator',
        ),
        migrations.RemoveField(
            model_name='measurement',
            name='data',
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
            name='data',
            field=jsonfield.fields.JSONField(help_text='Data produced by the job.', null=True, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='measurement',
            name='metadata',
            field=jsonfield.fields.JSONField(help_text='Measurement metadata', null=True, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='metric',
            name='parameters',
            field=jsonfield.fields.JSONField(help_text='Parameters used to define the metric', null=True, blank=True, default=None),
        ),
        migrations.AddField(
            model_name='metric',
            name='reference',
            field=jsonfield.fields.JSONField(help_text='Metric reference', default=None),
        ),
        migrations.AddField(
            model_name='metric',
            name='specs',
            field=jsonfield.fields.JSONField(help_text='Metric specification', default=None),
        ),
        migrations.AddField(
            model_name='metric',
            name='unit',
            field=models.CharField(null=True, blank=True, max_length=16, default=''),
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
            field=models.CharField(help_text='Metric name', primary_key=True, max_length=16, serialize=False),
        ),
    ]
