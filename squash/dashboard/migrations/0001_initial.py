# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('ci_id', models.CharField(help_text='Jenkins job ID', max_length=16)),
                ('ci_name', models.CharField(help_text='Name of the Jenkins project,e.g. validate_drp', max_length=32)),
                ('ci_dataset', models.CharField(help_text='Name of the dataset, e.g cfht', max_length=16)),
                ('ci_label', models.CharField(help_text='Name of the platform, eg. centos-7', max_length=16)),
                ('date', models.DateTimeField(help_text='Datetime when job was registered', auto_now=True)),
                ('ci_url', models.URLField(help_text='Jenkins job URL')),
                ('status', models.SmallIntegerField(help_text='Job status, 0=OK, 1=Failed', default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('value', django_mysql.models.DynamicField()),
                ('job', models.ForeignKey(related_name='measurements', to='dashboard.Job')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('metric', models.CharField(primary_key=True, max_length=16, serialize=False)),
                ('description', models.TextField()),
                ('units', models.CharField(max_length=16)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.SlugField(help_text='EUPS package name', max_length=64)),
                ('git_url', models.URLField(help_text='Git repo URL for package', max_length=128)),
                ('git_commit', models.CharField(help_text='SHA1 hash of the git commit', max_length=40)),
                ('git_branch', models.TextField(help_text='Resolved git branch that the commit resides on')),
                ('build_version', models.TextField(help_text='EUPS build version')),
                ('job', models.ForeignKey(related_name='packages', to='dashboard.Job')),
            ],
        ),
        migrations.AddField(
            model_name='measurement',
            name='metric',
            field=models.ForeignKey(to='dashboard.Metric'),
        ),
    ]
