import json
from django.db import models
from django.contrib.auth.models import User
from .bokeh_utils import update_bokeh_sessions


class Job(models.Model):
    """Job information"""
    STATUS_OK = 0
    STATUS_FAILED = 1

    name = models.CharField(max_length=32, blank=False)
    build = models.CharField(max_length=16, blank=False)
    runtime = models.DateTimeField(auto_now=True)
    url = models.TextField(null=False)
    status = models.SmallIntegerField(default=STATUS_OK)

    def get_jobs(self):
        pass

    def __str__(self):
        return self.build


class Package(models.model):
    """Software package (generally an Eups package, e.g., `afw`)."""
    # e.g. 'afw'
    name = models.TextField()
    # e.g. https://github.com/lsst/afw.git
    git_url = models.TextField()

    def __str__(self):
        return json.dumps({'_class': 'Package',
                           'name': self.name,
                           'git_url': self.git_url},
                          indent=2, sort_keys=True)


class PackageVersion(models.Model):
    """Version information of an Eups Product used in a Job."""
    job = models.ForeignKey(Job, null=False)
    package = models.ForeignKey(Package, null=False)
    # SHA1 hash of the git commit
    git_commit = models.CharField(max_length=40, null=False)
    # resolved git branch that the commit resides on
    git_branch = models.TextField()
    # Eups version information
    build_version = models.TextField()

    def __str__(self):
        return json.dumps({'_class': 'PackageVersion',
                           'job.build': self.job.build,
                           'package.name': self.package.name,
                           'git_commit': self.git_commit,
                           'git_branch': self.git_branch,
                           'build_version': self.build_version},
                          indent=2, sort_keys=True)


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
