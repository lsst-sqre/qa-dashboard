from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.conf import settings
from rest_framework import authentication, permissions,\
    viewsets, filters, response, status

from rest_framework_extensions.cache.mixins import CacheResponseMixin

from bokeh.embed import autoload_server

from .forms import JobFilter
from .models import Job, Metric, Measurement, VersionedPackage
from .serializers import JobSerializer, MetricSerializer,\
    RegressionSerializer, MeasurementSerializer, \
    BlobSerializer

try:
    bokeh_url = settings.BOKEH_URL
except AttributeError:
    # if not specified use the default which is localhost:5006
    bokeh_url = 'default'


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
        permissions.IsAuthenticatedOrReadOnly,
    )

    paginate_by = 100
    # list of available filter_backends, will enable these for all ViewSets
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class JobViewSet(DefaultsMixin, CacheResponseMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating jobs"""

    queryset = Job.objects.\
        prefetch_related('packages', 'measurements').order_by('date')
    serializer_class = JobSerializer
    filter_class = JobFilter
    search_fields = ('ci_id',)
    ordering_fields = ('date',)


class MeasurementViewSet(DefaultsMixin, CacheResponseMixin,
                         viewsets.ModelViewSet):
    """API endpoint consumed by the monitor app"""

    queryset = Measurement.objects.\
        prefetch_related('job', 'metric').order_by('job__date')
    serializer_class = RegressionSerializer
    filter_fields = ('job__ci_dataset', 'metric')


class MetricViewSet(DefaultsMixin, CacheResponseMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating metrics"""

    queryset = Metric.objects.order_by('metric')
    serializer_class = MetricSerializer

    def create(self, request, *args, **kwargs):
        # many=True for adding multiple items at once
        serializer = self.get_serializer(data=request.data,
                                         many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    search_fields = ('metric', )
    ordering_fields = ('metric',)


class DatasetViewSet(DefaultsMixin, viewsets.ViewSet):
    """API endpoint for listing datasets"""

    def list(self, request):
        datasets = Job.objects.values_list('ci_dataset', flat=True).distinct()
        return response.Response(datasets)


class DefaultsViewSet(DefaultsMixin, viewsets.ViewSet):
    """
    API endpoint for listing default values used by
    the bokeh apps
    """

    def list(self, request):
        ci_id = Job.objects.latest('pk').ci_id
        job__ci_dataset = Job.objects.latest('pk').ci_dataset
        metric = Metric.objects.latest('pk').metric
        snr_cut = '100'
        window = 'months'
        result = {'ci_id': ci_id, 'job__ci_dataset': job__ci_dataset,
                  'metric': metric, 'snr_cut': snr_cut,
                  'window': window}

        return response.Response(result)


# TODO: reduce code duplication in AMxViewSet and PAxViewSet

class AMxViewSet(DefaultsMixin, CacheResponseMixin, viewsets.ViewSet):
    """API endpoint for listing AMx app data"""

    def list(self, request):

        # TODO: filter by job id
        job = Job.objects.latest('pk')
        blob_serializer = BlobSerializer(job)

        # TODO: filter by metric
        measurement = Measurement.objects.filter(job=job)[0]
        measurement_serializer = MeasurementSerializer(measurement)

        data = {}
        metadata = {}

        if measurement_serializer.data['metadata']:

            metadata['metadata'] = \
                eval(measurement_serializer.data['metadata'])

            # datasets used in this measurement
            blobs = metadata['metadata'].pop('blobs')

            matched_dataset_id = blobs['matchedDataset']
            astrom_model_id = blobs['astromModel']

            # given the dataset ids, get the actual data
            # from the Job model
            data_blobs = eval(blob_serializer.data['blobs'])

            for blob in data_blobs:
                if blob['identifier'] == matched_dataset_id:
                    data['matchedDataset'] = blob['data']
                elif blob['identifier'] == astrom_model_id:
                    data['astromModel'] = blob['data']

        return response.Response({**data, **metadata}) # noqa


class PAxViewSet(DefaultsMixin, CacheResponseMixin, viewsets.ViewSet):
    """API endpoint for listing PAx app data"""

    def list(self, request):

        # TODO: filter by job id
        job = Job.objects.latest('pk')
        blob_serializer = BlobSerializer(job)

        # TODO: filter by metric
        measurement = Measurement.objects.filter(job=job)[0]
        measurement_serializer = MeasurementSerializer(measurement)

        data = {}
        metadata = {}

        if measurement_serializer.data['metadata']:

            metadata['metadata'] =\
                eval(measurement_serializer.data['metadata'])

            # datasets used in this measurement
            blobs = metadata['metadata'].pop('blobs')

            # data blob identifier for this measurement
            matched_dataset_id = blobs['matchedDataset']
            photom_model_id = blobs['photomModel']

            # given the dataset ids, get the actual data
            # from the Job model
            data_blobs = eval(blob_serializer.data['blobs'])

            for blob in data_blobs:
                if blob['identifier'] == matched_dataset_id:
                    data['matchedDataset'] = blob['data']
                elif blob['identifier'] == photom_model_id:
                    data['photomModel'] = blob['data']

        return response.Response({**data, **metadata})


def embed_bokeh(request, bokeh_app):
    """Render the requested app from the bokeh server"""

    # http://bokeh.pydata.org/en/0.12.3/docs/reference/embed.html

    # TODO: test if bokeh server is reachable
    bokeh_script = autoload_server(None, app_path="/{}".format(bokeh_app),
                                   url=bokeh_url)

    template = loader.get_template('dashboard/embed_bokeh.html')

    context = {'bokeh_script': bokeh_script,
               'bokeh_app': bokeh_app}

    response = HttpResponse(template.render(context, request))
    response.set_cookie('django_full_path', request.get_full_path())

    return response


def home(request):
    """Render the home page"""

    n_metrics = len(Metric.objects.all())
    job = Job.objects.latest('pk')
    n_packages = len(VersionedPackage.objects.filter(job=job))
    n_jobs = len(Job.objects.all())
    n_meas = len(Measurement.objects.all())

    datasets = Job.objects.values_list('ci_dataset', flat=True).distinct()
    last = Job.objects.latest('pk').date

    context = {"n_metrics": n_metrics,
               "n_packages": n_packages,
               "n_jobs": n_jobs,
               "n_meas": n_meas,
               "datasets": ", ".join(datasets),
               "last": last}

    return render(request, 'dashboard/index.html', context)
