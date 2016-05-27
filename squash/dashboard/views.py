from django.views.generic import ListView
from rest_framework import authentication, permissions, viewsets
from .viz.metrics import make_time_series_plot
from .bokeh_utils import get_bokeh_script
from .models import Job, Metric
from .serializers import JobSerializer, MetricSerializer


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

    queryset = Job.objects.order_by('ci_name')
    serializer_class = JobSerializer


class MetricViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating metrics"""

    queryset = Metric.objects.order_by('metric')
    serializer_class = MetricSerializer


class HomeView(ListView):
    model = Metric
    template_name = 'dashboard/index.html'


class ListMetricsView(ListView):
    model = Metric
    template_name = 'dashboard/metric.html'

    def get_context_data(self, **kwargs):

        context = super(ListMetricsView, self).get_context_data(**kwargs)
        selected_metric = self.kwargs['pk']
        context['selected_metric'] = selected_metric

        plot = make_time_series_plot(selected_metric)

        bokeh_script = get_bokeh_script(plot=plot)

        context.update(metric_script=bokeh_script)

        return context
