from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Job, Metric, Measurement


class JobSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('jobId', 'name', 'build', 'start', 'duration', 'status','links',)

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('job-detail', kwargs={'pk': obj.pk}, request=request),
        }


class MetricSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField()

    class Meta:
        model = Metric
        fields = ('metricId', 'name', 'description', 'units', 'condition', 'minimum', 'design', 'stretch', 'user', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('metric-detail', kwargs={'pk': obj.pk}, request=request),
         }


class MeasurementSerializer(serializers.ModelSerializer):

    links = serializers.SerializerMethodField()

    class Meta:
        model = Measurement
        fields = ('measurementId', 'jobId', 'metricId', 'value', 'links',)

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('measurement-detail', kwargs={'pk': obj.pk}, request=request),
        }