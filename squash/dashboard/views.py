from rest_framework import authentication, permissions, viewsets
from .models import Job, Metric, Measurement
from .serializers import JobSerializer, MetricSerializer, MeasurementSerializer


class DefaultsMixin(object):
    """
    Default settings for view authentication, permissions,
    filtering and pagination.
    """

    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    paginate_by = 25
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class JobViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating jobs"""

    queryset = Job.objects.order_by('jobId')
    serializer_class = JobSerializer


class MetricViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating metrics"""

    queryset = Metric.objects.order_by('metricId')
    serializer_class = MetricSerializer


class MeasurementViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating measurements"""

    queryset = Measurement.objects.order_by('measurementId')
    serializer_class = MeasurementSerializer
