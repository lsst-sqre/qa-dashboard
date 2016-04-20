from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'job', views.JobViewSet)
router.register(r'metric', views.MetricViewSet)
router.register(r'measurement', views.MeasurementViewSet)
