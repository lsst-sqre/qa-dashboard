from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from rest_framework import authentication, permissions, viewsets
from .models import Job, Metric
from .serializers import JobSerializer, MetricSerializer

from .bokeh_utils import get_bokeh_script
from .viz.metrics import make_metric_plot


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

    queryset = Job.objects.order_by('name')
    serializer_class = JobSerializer


class MetricViewSet(DefaultsMixin, viewsets.ModelViewSet):
    """API endpoint for listing and creating metrics"""

    queryset = Metric.objects.order_by('metric')
    serializer_class = MetricSerializer


class HomeView(TemplateView):
    template_name = 'dashboard/index.html'


class MetricDashboardView(DetailView):
    template_name = 'dashboard/metric.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(MetricDashboardView, self).get_context_data(**kwargs)
        context.update(
            dashboard='metric'
        )
        plot = make_metric_plot(user=self.object)
        metric_script = get_bokeh_script(user=self.object,
                                         plot=plot,
                                         suffix='metric')
        context.update(metric_script=metric_script)
        return context
