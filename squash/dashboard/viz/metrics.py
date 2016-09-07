import os
import requests
from datetime import datetime
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool,\
                         Span, Label
from bokeh.models.widgets import Select
from bokeh.layouts import row, widgetbox
from defaults import init_time_series_plot, init_legend

SQUASH_API_URL = os.environ.get('SQUASH_API_URL',
                                'http://localhost:8000/dashboard/api')


class Metrics(object):
    '''Display a time series plot for the selected dataset and metric'''

    def __init__(self):

        self.api = requests.get(SQUASH_API_URL).json()
        self.source = ColumnDataSource(data={'x': [], 'y': [], 'desc': [],
                                             'ci_url': [], 'units': []})
        self.create_layout()

    def create_layout(self):
        """the app has select widgets for datasets,
         metrics and a plot"""

        self.get_datasets()

        # dataset widget
        dataset_select = Select(title="Data Set:", value=self.selected_dataset,
                                options=self.datasets, width=100)

        dataset_select.on_change("value", self.on_dataset_change)

        self.get_metrics()

        # metric widget
        metric_select = Select(title="Metric:", value=self.selected_metric,
                               options=self.metrics, width=100)

        metric_select.on_change("value", self.on_metric_change)

        # measurements for the selected dataset has values
        # for all the metrics, we keep them all and filter
        # by the selected metric

        # handle empty results
        if self.selected_dataset and self.selected_metric:
            self.get_measurements()

        # plot with hover and tap tool

        hover = HoverTool(tooltips=[("Build ID", "@desc"),
                                    ("Value", "@y (@units)")])

        self.plot = init_time_series_plot(hover=hover)

        measurements = self.plot.line(
            x='x', y='y', source=self.source,
            line_width=2, color='black',
        )

        self.legends = [("Measurements", [measurements])]

        self.plot.circle(x='x', y='y', source=self.source,
                         color="black", fill_color="white", size=16)

        # set a tap tool to link with ci_url
        tap = self.plot.select(type=TapTool)

        tap.callback = OpenURL(url="@ci_url")

        # set axis labels, legend and compose the final layout
        self.plot.yaxis.axis_label = self.selected_metric +\
            ' (' + self.units[self.selected_metric] + ')'

        # TODO: add a checkbox to control this

        self.annotations = {}

        for t in self.thresholds:
            self.annotations[t] = self.draw_annotations(self.thresholds[t])

        self.layout = row(widgetbox(dataset_select,
                                    metric_select, width=150), self.plot)

    def get_datasets(self):
        self.datasets = requests.get(self.api['datasets']).json()

        if self.datasets:
            self.selected_dataset = self.datasets[0]
        else:
            self.selected_dataset = None

    def on_dataset_change(self, attr, old, new):
        self.selected_dataset = new
        # when a new dataset is selected we have to
        # retrieve the measurements again
        self.get_measurements()

    def get_metrics(self):

        # TODO: we should get only the metrics actually computed

        r = requests.get(self.api['metrics']).json()

        self.metrics = [x['metric'] for x in r['results']]

        # handle empty results
        if self.metrics:

            self.units = dict(zip(self.metrics,
                                  [x['units'] for x in r['results']]))

            # select first metric by default
            self.selected_metric = self.metrics[0]

            # configure thresholds for each metric

            self.thresholds = {}

            minimum = dict(zip(self.metrics,
                               [x['minimum'] for x in r['results']]))
            self.thresholds['minimum'] = {'values': minimum,
                                          'text': 'Minimum Specification',
                                          'color': 'red'}

            design = dict(zip(self.metrics,
                              [x['design'] for x in r['results']]))
            self.thresholds['design'] = {'values': design,
                                         'text': 'Design Specification',
                                         'color': 'blue'}

            stretch = dict(zip(self.metrics,
                               [x['stretch'] for x in r['results']]))
            self.thresholds['stretch'] = {'values': stretch,
                                          'text': 'Strecth goal',
                                          'color': 'green'}

        else:
            self.selected_metric = None

    def on_metric_change(self, attr, old, new):

        # Update plot threshold annotations and axis labels

        for t in self.annotations:
            self.annotations[t]['span'].location = \
                self.thresholds[t]['values'][new]
            self.annotations[t]['label'].y = self.thresholds[t]['values'][new]
            self.annotations[t]['arrow'].y = self.thresholds[t]['values'][new]

        self.selected_metric = new

        self.plot.yaxis.axis_label = self.selected_metric\
            + '(' + self.units[self.selected_metric] + ')'

        size = len(self.dates)
        units = [self.units[self.selected_metric]] * size

        # update the data source and the plot will automatically update
        self.source.data = dict(x=self.dates,
                                y=[m['value'] for m in self.measurements if
                                   m['metric'] == self.selected_metric],
                                desc=self.ci_id, ci_url=self.ci_url,
                                units=units, )

    def get_measurements(self):

        # e.g. http://localhost:8000/dashboard/api/jobs/?ci_dataset=cfht
        r = requests.get(self.api['jobs'],
                         params={'ci_dataset': self.selected_dataset}).json()

        # results are paginated, walk through each page

        # TODO: figure out how to retrieve number of pages in drf
        count = r['count']

        page_size = len(r['results'])

        jobs = []

        if page_size > 0:

            num_pages = int(count/page_size) + (count % page_size > 0)

            for page in range(1, num_pages + 1):
                jobs.extend(requests.get(
                    self.api['jobs'],
                    params={'ci_dataset': self.selected_dataset,
                            'page': page}).json()['results'])

        # filter out failed jobs, i.e jobs that have
        # incomplete measurements. This should be done by looking
        # at the job status, but for now it is useless

        jobs = [job for job in jobs
                if len(job['measurements']) == len(self.metrics)]

        self.ci_id = [int(job['ci_id']) for job in jobs]

        # 2016-08-10T05:22:37.700146Z
        # DM-7517 job api return is sorted by date

        self.dates = [datetime.strptime(job['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                      for job in jobs]

        # create a flat list with all measurements
        # [ {"metric" : "AM1", "value" : 3.0}, ... ]
        self.measurements = []

        for job in jobs:
            for sublist in job['measurements']:
                self.measurements.append(sublist)

        self.ci_url = [job['ci_url'] for job in jobs]

        size = len(self.dates)
        units = [self.units[self.selected_metric]] * size

        # measurements are filtered by metric
        self.source.data = dict(x=self.dates,
                                y=[m['value'] for m in self.measurements
                                   if m['metric'] == self.selected_metric],
                                desc=self.ci_id, ci_url=self.ci_url,
                                units=units, )

    def draw_annotations(self, threshold):

        location = threshold['values'][self.selected_metric]
        color = threshold['color']

        span = Span(location=location, dimension='width',
                    line_width=1, line_color=color, line_dash='dotted',)

        self.plot.add_layout(span)

        text = threshold['text']
        label = Label(x=70, y=location, x_units='screen',
                      y_units='data', text=text, text_color=color,
                      text_font_size='11pt', text_font_style='normal',
                      render_mode='css')

        self.plot.add_layout(label)

        arrow = Label(x=100, y=location, x_units='screen',
                      y_units='data', text="&darr;",
                      text_color=color, text_font_size='24pt',
                      text_font_style='normal',
                      render_mode='css', y_offset=-35)

        self.plot.add_layout(arrow)

        return {'span': span, 'label': label, 'arrow': arrow}


curdoc().add_root(Metrics().layout)
curdoc().title = "SQUASH"
