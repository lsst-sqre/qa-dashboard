from django.db import models
from django.contrib.auth.models import User
from .bokeh_utils import update_bokeh_sessions


class Job(models.Model):
    """Job information"""
    STATUS_OK = 0
    STATUS_FAILED = 1

    name = models.CharField(max_length=32, blank=False,
                            help_text='Name of Job')
    build = models.CharField(max_length=16, blank=False,
                             help_text='Jenkins job ID')
    runtime = models.DateTimeField(auto_now=True,
                                   help_text='Datetime when job was run')
    url = models.TextField(null=False, help_text='Jenkins job URL')
    status = models.SmallIntegerField(default=STATUS_OK,
                                      help_text='Job status, 0=OK, 1=Failed')

    def get_jobs(self):
        pass

    def __str__(self):
        return self.build


class Metric(models.Model):
    """Metric information"""
    metric = models.CharField(max_length=16, primary_key=True)
    description = models.TextField()
    units = models.CharField(max_length=16)
    condition = models.CharField(max_length=2, blank=False, default='<')
    minimum = models.FloatField(null=False)
    design = models.FloatField(null=False)
    stretch = models.FloatField(null=False)
    user = models.FloatField(null=False)

    def __str__(self):
        return self.metric


class Measurement(models.Model):
    """Measurement of a metric by a process"""
    metric = models.ForeignKey(Metric, null=False)
    job = models.ForeignKey(Job, null=False, related_name='measurements')
    value = models.FloatField(blank=False)

    def __float__(self):
        return self.value

    def save(self, *args, **kwargs):
        super(Measurement, self).save(*args, **kwargs)
        # When a new measurement is saved, update all the data
        # for the bokeh sessions.
        # Improvements:
        # - Only update metrics affected by this data
        # (only get affected Sessions)
        update_bokeh_sessions(UserSession.objects.all())


class UserSession(models.Model):
    user = models.ForeignKey(User, null=False)
    bokehSessionId = models.CharField(max_length=64)
