from ast import literal_eval

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
    RegressionSerializer


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

    def get_defaults(self):
        queryset = Job.objects.values('ci_id', 'ci_dataset').latest('pk')

        ci_id = queryset['ci_id']
        ci_dataset = queryset['ci_dataset']

        queryset = Metric.objects.values_list('metric', flat=True)

        if 'AM1' in queryset:
            metric = 'AM1'
        else:
            metric = queryset.latest('pk')

        snr_cut = '100'
        window = 'months'

        return {'ci_id': ci_id, 'ci_dataset': ci_dataset,
                'metric': metric, 'snr_cut': snr_cut,
                'window': window}

    def list(self, request):
        defaults = self.get_defaults()
        return response.Response(defaults)


class BokehAppViewSet(DefaultsMixin, viewsets.ViewSet):

    def get_app_data(self, ci_id, ci_dataset, metric):

        data = {}

        blobs = Job.objects.filter(ci_id=ci_id,
                                   ci_dataset=ci_dataset).values('blobs')

        metadata = Measurement.\
            objects.filter(metric=metric, job__ci_id=ci_id,
                           job__ci_dataset=ci_dataset).values('metadata')

        if metadata.exists():
            # workaround for getting item from queryset
            metadata = metadata[0]['metadata']
            if metadata:
                metadata = literal_eval(literal_eval(metadata))
                blob_id = metadata.pop('blobs')
                data['metadata'] = metadata

                if blobs.exists():
                    # workaround for getting item from queryset
                    blobs = blobs[0]['blobs']
                    if blobs:
                        blobs = literal_eval(literal_eval(blobs))
                        for blob in blobs:
                            # Look up for data blobs
                            if blob['identifier'] == blob_id['matchedDataset']:
                                data['matchedDataset'] = blob['data']

                            elif blob['identifier'] == blob_id['photomModel']:
                                data['photomModel'] = blob['data']

                            elif blob['identifier'] == blob_id['astromModel']:
                                data['astromModel'] = blob['data']
        return data

    def list(self, request):

        defaults = DefaultsViewSet().get_defaults()

        ci_id = self.request.query_params.get('ci_id',
                                              defaults['ci_id'])

        ci_dataset = self.request.query_params.get('ci_dataset',
                                                   defaults['ci_dataset'])
        metric = self.request.query_params.get('metric',
                                               defaults['metric'])

        data = self.get_app_data(ci_id, ci_dataset, metric)

        return response.Response(data)


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

    # Save full url path in the HTTP response, so that the bokeh
    # app can use this info, e.g:
    # http://localhost:8000/dashboard/AMx/?metric=AM1&ci_dataset=cfht&ci_id=452

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
