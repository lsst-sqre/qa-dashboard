from django.views.generic import ListView
from rest_framework import authentication, permissions,\
    viewsets, filters, response
from .forms import JobFilter
from .models import Job, Metric, Measurement
from .serializers import JobSerializer, MetricSerializer, MetricsAppSerializer
from bokeh.embed import autoload_server
from django.conf import settings

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


class JobViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating jobs"""

    queryset = Job.objects.order_by('date')
    serializer_class = JobSerializer
    filter_class = JobFilter
    search_fields = ('ci_id',)
    ordering_fields = ('date',)


class MetricsAppViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """ API endpoint consumed by the metrics app"""

    queryset = Measurement.objects.order_by('job__date')
    serializer_class = MetricsAppSerializer
    filter_fields = ('job__ci_dataset', 'metric')


class MetricViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating metrics"""

    queryset = Metric.objects.order_by('metric')
    serializer_class = MetricSerializer
    search_fields = ('metric', )
    ordering_fields = ('metric',)


class DatasetViewSet(DefaultsMixin, viewsets.ViewSet):
    """API endpoint for listing datasets"""

    def list(self, request):
        datasets = Job.objects.values_list('ci_dataset', flat=True).distinct()
        return response.Response(datasets)


class HomeView(ListView):
    model = Metric
    template_name = 'dashboard/index.html'


class MetricsView(ListView):
    model = Metric
    template_name = 'dashboard/metrics.html'

    def get_context_data(self, **kwargs):
        context = super(MetricsView, self).get_context_data(**kwargs)

        astrometry_bokeh_script = autoload_server(None,
                                                  app_path="/astrometry",
                                                  url=bokeh_url)
        photometry_bokeh_script = autoload_server(None,
                                                  app_path="/photometry",
                                                  url=bokeh_url)
        regression_bokeh_script = autoload_server(None,
                                                  app_path="/regression",
                                                  url=bokeh_url)

        context.update(astrometry_bokeh_script=astrometry_bokeh_script,
                       photometry_bokeh_script=photometry_bokeh_script,
                       regression_bokeh_script=regression_bokeh_script)
        return context
