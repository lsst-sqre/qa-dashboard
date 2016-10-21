from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from . import views
admin.site.site_header = 'SQUASH Admin'

api_router = DefaultRouter()
api_router.register(r'jobs', views.JobViewSet)
api_router.register(r'metrics', views.MetricViewSet)
api_router.register(r'measurements', views.MetricsAppViewSet,
                    base_name='measurements')
api_router.register(r'datasets', views.DatasetViewSet, base_name='datasets')

urlpatterns = [
    url(r'^dashboard/api/', include(api_router.urls)),
    url(r'^dashboard/admin', include(admin.site.urls)),
    url(r'^dashboard/api/token', obtain_auth_token, name='api-token'),
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^(?P<pk>[a-zA-Z0-9]*$)', views.MetricsView.as_view(),
        name='metrics-list')

]
