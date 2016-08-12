import os
import requests
from datetime import datetime
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool
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
                                             'ci_url': [], 'units': [],
                                             'minimum': [], 'design': [],
                                             'stretch': []})
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

        self.draw_spec_annotations()

        self.layout = row(widgetbox(dataset_select,
                                    metric_select, width=150), self.plot)

    def get_datasets(self):
        self.datasets = requests.get(self.api['datasets']).json()
        self.selected_dataset = self.datasets[0]

    def on_dataset_change(self, attr, old, new):
        self.selected_dataset = new
        # when a new dataset is selected we have to
        # retrieve the measurements again
        self.get_measurements()

    def get_metrics(self):

        # TODO: we should get only the metrics actually computed

        r = requests.get(self.api['metrics']).json()

        self.metrics = [x['metric'] for x in r['results']]

        # in case metrics is and empty list
        if self.metrics:

            self.units = dict(zip(self.metrics,
                                  [x['units'] for x in r['results']]))
            self.minimum = dict(zip(self.metrics,
                                    [x['minimum'] for x in r['results']]))
            self.design = dict(zip(self.metrics,
                                   [x['design'] for x in r['results']]))
            self.stretch = dict(zip(self.metrics,
                                    [x['stretch'] for x in r['results']]))

        # default metric is the first one
        self.selected_metric = self.metrics[0]

    def on_metric_change(self, attr, old, new):

        self.selected_metric = new

        self.plot.yaxis.axis_label = self.selected_metric\
            + '(' + self.units[self.selected_metric] + ')'

        # need these values to draw the spec thresholds
        size = len(self.dates)
        units = [self.units[self.selected_metric]] * size
        minimum = [self.minimum[self.selected_metric]] * size
        design = [self.design[self.selected_metric]] * size
        stretch = [self.stretch[self.selected_metric]] * size

        # update the data source and the plot will automatically update
        self.source.data = dict(x=self.dates,
                                y=[m['value'] for m in self.measurements if
                                   m['metric'] == self.selected_metric],
                                desc=self.ci_id, ci_url=self.ci_url,
                                units=units, minimum=minimum, design=design,
                                stretch=stretch, )

    def get_measurements(self):

        # e.g. http://localhost:8000/dashboard/api/jobs/?ci_dataset=cfht
        self.jobs = requests.get(self.api['jobs'] + '?ci_dataset=' +
                                 self.selected_dataset).json()['results']

        self.ci_id = [job['ci_id'] for job in self.jobs]

        # 2016-08-10T05:22:37.700146Z
        self.dates = [datetime.strptime(job['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                      for job in self.jobs]

        # create a flat list with all measurements
        # [ {"metric" : "AM1", "value" : 3.0}, ... ]
        self.measurements = []

        for job in self.jobs:
            for sublist in job['measurements']:
                self.measurements.append(sublist)

        self.ci_url = [job['ci_url'] for job in self.jobs]

        size = len(self.dates)
        units = [self.units[self.selected_metric]] * size
        minimum = [self.minimum[self.selected_metric]] * size
        design = [self.design[self.selected_metric]] * size
        stretch = [self.stretch[self.selected_metric]] * size

        # measurements are filtered by metric
        self.source.data = dict(x=self.dates,
                                y=[m['value'] for m in self.measurements
                                   if m['metric'] == self.selected_metric],
                                desc=self.ci_id, ci_url=self.ci_url,
                                units=units, minimum=minimum, design=design,
                                stretch=stretch,)

    def draw_spec_annotations(self):

        minimum = self.plot.line(x='x', y='minimum', source=self.source,
                                 line_width=1, color='red',
                                 line_dash='dotted',)
        self.legends.append(("Minimum spec", [minimum]))

        design = self.plot.line(x='x', y='design', source=self.source,
                                line_width=1, color='blue',
                                line_dash='dotted',)

        self.legends.append(("Design spec", [design]))

        stretch = self.plot.line(x='x', y='stretch', source=self.source,
                                 line_width=1, color='green',
                                 line_dash='dotted',)
        self.legends.append(("Stretch goal", [stretch]))

        self.plot.add_layout(init_legend(legends=self.legends))


curdoc().add_root(Metrics().layout)
curdoc().title = "SQUASH"
