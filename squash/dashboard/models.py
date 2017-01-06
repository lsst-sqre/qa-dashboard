import json
from django.db import models
from django_mysql.models import DynamicField, Model


class Job(models.Model):
    """Job information"""
    STATUS_OK = 0
    STATUS_FAILED = 1

    ci_id = models.CharField(max_length=16, blank=False,
                             help_text='Jenkins job ID')
    ci_name = models.CharField(max_length=32, blank=False,
                               help_text='Name of the Jenkins project,'
                                         'e.g. validate_drp')
    ci_dataset = models.CharField(max_length=16, blank=False,
                                  help_text='Name of the dataset, e.g cfht')
    ci_label = models.CharField(max_length=16, blank=False,
                                help_text='Name of the platform, eg. centos-7')
    date = models.DateTimeField(auto_now=True,
                                help_text='Datetime when job was registered')
    ci_url = models.URLField(null=False, help_text='Jenkins job URL')
    status = models.SmallIntegerField(default=STATUS_OK,
                                      help_text='Job status, 0=OK, 1=Failed')

    def get_jobs(self):
        pass

    def __str__(self):
        return self.ci_id


class VersionedPackage(models.Model):
    """A specific version of an Eups Product used in a Job."""
    name = models.SlugField(
        max_length=64, null=False,
        help_text='EUPS package name')
    git_url = models.URLField(
        max_length=128,
        help_text='Git repo URL for package')
    git_commit = models.CharField(
        max_length=40, null=False,
        help_text='SHA1 hash of the git commit')
    git_branch = models.TextField(
        help_text='Resolved git branch that the commit resides on')
    build_version = models.TextField(
        help_text='EUPS build version')

    job = models.ForeignKey(Job, null=False, related_name='packages')

    def __str__(self):
        return json.dumps({'_class': 'VersionedPackage',
                           'job.ci_id': self.job.ci_id,
                           'name': self.name,
                           'git_url': self.git_url,
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


class Measurement(Model):
    """Measurement of a metric by a process"""
    metric = models.ForeignKey(Metric, null=False)
    job = models.ForeignKey(Job, null=False, related_name='measurements')
    value = DynamicField(spec={'test1': str})

    def __float__(self):
        return self.value
