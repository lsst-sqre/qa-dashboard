import django_filters
from .models import Job


class JobFilter(django_filters.FilterSet):
    class Meta:
        model = Job
        fields = ('ci_id', 'ci_dataset', 'ci_label', 'packages')
