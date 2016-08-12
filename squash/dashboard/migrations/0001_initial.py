# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('ci_name', models.CharField(max_length=32, help_text='Name of the Jenkins job')),
                ('ci_id', models.CharField(max_length=16, help_text='Jenkins job ID')),
                ('date', models.DateTimeField(help_text='Datetime when job was registered', auto_now=True)),
                ('ci_url', models.URLField(help_text='Jenkins job URL')),
                ('status', models.SmallIntegerField(default=0, help_text='Job status, 0=OK, 1=Failed')),
            ],
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField()),
                ('job', models.ForeignKey(related_name='measurements', to='dashboard.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('metric', models.CharField(serialize=False, max_length=16, primary_key=True)),
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
            name='UserSession',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('bokehSessionId', models.CharField(max_length=64)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VersionedPackage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.SlugField(max_length=64, help_text='EUPS package name')),
                ('git_url', models.URLField(max_length=128, help_text='Git repo URL for package')),
                ('git_commit', models.CharField(max_length=40, help_text='SHA1 hash of the git commit')),
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
