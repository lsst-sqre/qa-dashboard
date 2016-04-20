from django.db import models


class Job(models.Model):
    """Job information"""
    STATUS_OK = 0
    STATUS_FAILED = 1

    jobId = models.AutoField(primary_key=True)
    name = models.DateTimeField()
    build = models.CharField(max_length=16, blank=False)
    start = models.DateTimeField()
    duration = models.DateTimeField()
    status = models.SmallIntegerField(default=STATUS_OK)

    def __str__(self):
        return self.build


class Metric(models.Model):
    """Metric information"""
    metricId = models.AutoField(primary_key=True)
    name = models.TextField(blank=False, unique=True)
    description = models.TextField()
    units = models.CharField(max_length=16)
    condition = models.CharField(max_length=2, blank=False, default='<')
    minimum = models.FloatField(null=False)
    design = models.FloatField(null=False)
    stretch = models.FloatField(null=False)
    user = models.FloatField(null=False)

    def __str__(self):
        return self.name


class Measurement(models.Model):
    """Measurement of a metric by a process"""
    measurementId = models.AutoField(primary_key=True)
    jobId = models.ForeignKey(Job, null=False)
    metricId = models.ForeignKey(Metric, null=False)
    value = models.FloatField(null=False)

    def __str__(self):
        return self.value
