# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('ci_id', models.CharField(max_length=16, help_text='Jenkins job ID')),
                ('ci_name', models.CharField(max_length=32, help_text='Name of the Jenkins project,e.g. validate_drp')),
                ('ci_dataset', models.CharField(max_length=16, help_text='Name of the dataset, e.g cfht')),
                ('ci_label', models.CharField(max_length=16, help_text='Name of the platform, eg. centos-7')),
                ('date', models.DateTimeField(auto_now=True, help_text='Datetime when job was registered')),
                ('ci_url', models.URLField(help_text='Jenkins job URL')),
                ('status', models.SmallIntegerField(default=0, help_text='Job status, 0=OK, 1=Failed')),
            ],
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.FloatField()),
                ('data', jsonfield.fields.JSONField(default=None, null=True, blank=True)),
                ('job', models.ForeignKey(to='dashboard.Job', related_name='measurements')),
            ],
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('metric', models.CharField(max_length=16, serialize=False, primary_key=True)),
                ('description', models.TextField()),
                ('units', models.CharField(max_length=16, blank=True)),
                ('condition', models.CharField(default='<', max_length=2)),
                ('minimum', models.FloatField()),
                ('design', models.FloatField()),
                ('stretch', models.FloatField()),
                ('user', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='VersionedPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.SlugField(max_length=64, help_text='EUPS package name')),
                ('git_url', models.URLField(max_length=128, help_text='Git repo URL for package')),
                ('git_commit', models.CharField(max_length=40, help_text='SHA1 hash of the git commit')),
                ('git_branch', models.TextField(help_text='Resolved git branch that the commit resides on')),
                ('build_version', models.TextField(help_text='EUPS build version')),
                ('job', models.ForeignKey(to='dashboard.Job', related_name='packages')),
            ],
        ),
        migrations.AddField(
            model_name='measurement',
            name='metric',
            field=models.ForeignKey(to='dashboard.Metric'),
        ),
    ]
