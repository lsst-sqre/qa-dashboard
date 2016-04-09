from django.contrib import admin
from .models import Dataset, Visit, Ccd

admin.site.register(Dataset)
admin.site.register(Visit)
admin.site.register(Ccd)
