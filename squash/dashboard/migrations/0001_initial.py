# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ccd',
            fields=[
                ('ccdId', models.AutoField(primary_key=True, serialize=False)),
                ('ccd', models.TextField()),
                ('llra', models.FloatField()),
                ('lldecl', models.FloatField()),
                ('urra', models.FloatField()),
                ('urdecl', models.FloatField()),
                ('medianSkyBkg', models.FloatField()),
                ('madSkyBkg', models.FloatField()),
                ('medianFwhm', models.FloatField()),
                ('madFwhm', models.FloatField()),
                ('medianR50', models.FloatField()),
                ('madR50', models.FloatField()),
                ('medianMajorAxis', models.FloatField()),
                ('madMajorAxis', models.FloatField()),
                ('medianMinorAxis', models.FloatField()),
                ('madMinorAxis', models.FloatField()),
                ('medianTheta', models.FloatField()),
                ('madTheta', models.FloatField()),
                ('medianScatterRa', models.FloatField()),
                ('madScatterRa', models.FloatField()),
                ('medianScatterDecl', models.FloatField()),
                ('madScatterDecl', models.FloatField()),
                ('medianScatterPsfFlux', models.FloatField()),
                ('madScatterPsfFlux', models.FloatField()),
                ('nSources', models.IntegerField()),
                ('nCosmicRays', models.IntegerField()),
                ('log', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('datasetId', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('camera', models.TextField()),
                ('description', models.TextField()),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('visitId', models.AutoField(primary_key=True, serialize=False)),
                ('visit', models.IntegerField()),
                ('mjd', models.IntegerField()),
                ('nExposures', models.IntegerField()),
                ('exposureType', models.TextField()),
                ('exposureStart', models.DateTimeField()),
                ('exposureTime', models.IntegerField()),
                ('filter', models.CharField(max_length=1)),
                ('telRa', models.FloatField()),
                ('telDecl', models.FloatField()),
                ('zenithDistance', models.FloatField()),
                ('airMass', models.FloatField()),
                ('hourAngle', models.FloatField()),
                ('datasetId', models.ForeignKey(to='dashboard.Dataset')),
            ],
        ),
        migrations.AddField(
            model_name='ccd',
            name='visitId',
            field=models.ForeignKey(to='dashboard.Visit'),
        ),
    ]
