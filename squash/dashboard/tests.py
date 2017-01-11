from django.test import TestCase
from .models import Job, Metric, Measurement


class JSONFieldTests(TestCase):
    """ Test insertion of JSON supported data types, uses fixtures to
        load initial data
    """
    fixtures = ['initial_data', 'test_data']

    def setUp(self):
        self.job = Job.objects.latest('id')
        self.metric = Metric.objects.latest('metric')

    def test_string(self):

        expected = "a string"
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

    def test_number(self):

        expected = 1
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

        expected = 1.0
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

    def test_boolean(self):

        expected = True
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

        expected = False
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

    def test_array(self):

        expected = ['an', 'array']
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

    def test_object(self):

        expected = {'an': 'object'}
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

    def test_empty_string(self):

        expected = ""
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)

    def test_null(self):

        expected = None
        Measurement.objects.create(job=self.job, metric=self.metric, value=0,
                                   data=expected)
        actual = Measurement.objects.latest('id').data

        self.assertEqual(actual, expected)
