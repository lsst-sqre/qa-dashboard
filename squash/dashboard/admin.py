from django.contrib import admin
from .models import Job, Metric, Measurement, VersionedPackage, UserSession

admin.site.register(Job)
admin.site.register(Metric)
admin.site.register(Measurement)
admin.site.register(VersionedPackage)
admin.site.register(UserSession)
