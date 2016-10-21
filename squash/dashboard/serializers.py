from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Job, Metric, Measurement, VersionedPackage
from django.db import transaction


class MetricSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField()

    class Meta:
        model = Metric
        fields = ('metric', 'description', 'units', 'condition',
                  'minimum', 'design', 'stretch', 'user', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('metric-detail', kwargs={'pk': obj.pk},
                            request=request),
         }


class MeasurementSerializer(serializers.ModelSerializer):
    """Serializer for `models.Measurement` objects.

    This serializer is intended to be nested inside the JobSerializer's
    `measurements` field.
    """

    class Meta:
        model = Measurement
        fields = ('metric', 'job', 'value')


class MetricsAppSerializer(serializers.ModelSerializer):

    ci_id = serializers.SerializerMethodField()
    ci_url = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    changed_packages = serializers.SerializerMethodField()

    class Meta:
        model = Measurement
        fields = ('value', 'ci_id', 'ci_url', 'date', "changed_packages")

    def get_ci_id(self, obj):
        return obj.job.ci_id

    def get_ci_url(self, obj):
        return obj.job.ci_url

    def get_date(self, obj):
        return obj.job.date

    def get_changed_packages(self, obj):

        current = []
        for pkg in VersionedPackage.objects.filter(job=obj.job):
            current.append({"git_url": pkg.git_url,
                            "git_commit": pkg.git_commit,
                            "ci_id": pkg.job.ci_id,
                            "name": pkg.name,
                            "build_version": pkg.build_version})

        try:
            previous_job = obj.job.get_previous_by_date()
            previous = []

            for pkg in VersionedPackage.objects.filter(job=previous_job):
                previous.append({"git_url": pkg.git_url,
                                 "git_commit": pkg.git_commit,
                                 "ci_id": pkg.job.ci_id,
                                 "name": pkg.name,
                                 "build_version": pkg.build_version})
        except:
            previous = current

        # TODO: return the list of packages that changed in a given job with
        # respect to the previous one by checking the diff in the git
        # commit sha of each package

        return {'previous_job': previous, 'current_job': current}


class VersionedPackageSerializer(serializers.ModelSerializer):
    """Serializer for `models.VersionedPackage` objects.

    This serializer is intended to be nested inside the JobSerializer; the
    `packages` in Jobs includes a list of VersionedPackages for all packages
    used in a Job.
    """

    class Meta:
        model = VersionedPackage
        fields = ('name', 'git_url', 'git_commit', 'git_branch',
                  'build_version')


class JobSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField()

    measurements = MeasurementSerializer(many=True)
    packages = VersionedPackageSerializer(many=True)

    class Meta:
        model = Job
        fields = ('ci_id', 'ci_name', 'ci_dataset', 'ci_label', 'date',
                  'ci_url', 'status', 'measurements', 'packages',
                  'links')

    # Override the create method to create nested objects from request data
    def create(self, data):
        measurements = data.pop('measurements')
        packages = data.pop('packages')

        # Use transactions, so that if one of the measurement objects isn't
        # valid that we will rollback even the parent Job object creation
        with transaction.atomic():
            job = Job.objects.create(**data)
            for measurement in measurements:
                Measurement.objects.create(job=job, **measurement)
            for package in packages:
                VersionedPackage.objects.create(job=job, **package)

        return job

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('job-detail', kwargs={'pk': obj.pk},
                            request=request),
        }
