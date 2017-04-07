from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views

admin.site.site_header = 'SQUASH Admin'

api_router = DefaultRouter()
api_router.register(r'jobs', views.JobViewSet)
api_router.register(r'metrics', views.MetricViewSet)
api_router.register(r'datasets', views.DatasetViewSet,
                    base_name='datasets')
api_router.register(r'defaults', views.DefaultsViewSet,
                    base_name='defaults')

# endpoints for data consumed by the bokeh apps
api_router.register(r'measurements', views.MeasurementViewSet,
                    base_name='measurements')
api_router.register(r'AMx', views.AMxViewSet, base_name='AMx')
api_router.register(r'PAx', views.PAxViewSet, base_name='PAx')

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^dashboard/api/', include(api_router.urls)),
    url(r'^dashboard/admin/', include(admin.site.urls)),
    url(r'^dashboard/(?P<bokeh_app>[\w./-]+)/$', views.embed_bokeh,
        name='embed-bokeh')
]
