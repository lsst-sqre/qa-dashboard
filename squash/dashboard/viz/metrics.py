from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool,\
                         Span, Label
from bokeh.models.widgets import Select
from bokeh.layouts import row, widgetbox
from defaults import init_time_series_plot
from service import get_datasets, get_metrics, get_measurements_by_dataset


class Metrics(object):
    """The metrics app consists of a time series plot showing measurements
    for a given selected dataset and metric.
    """

    def __init__(self):

        self.source = ColumnDataSource(data={'x': [], 'y': [], 'desc': [],
                                             'ci_url': [], 'units': [],})
        self.compose_layout()

    def compose_layout(self):
        """Compose the layout ot the app, the main elements are the widgets to
        select the dataset and the metric and a plot
        """
        self.datasets = get_datasets()

        # dataset select widget
        dataset_select = Select(title="Data Set:",
                                value=self.datasets['default'],
                                options=self.datasets['datasets'], width=100)

        dataset_select.on_change("value", self.on_dataset_change)

        self.metrics = get_metrics()
        self.selected_metric = self.metrics['default']

        # thresholds are used to make plot annotations for now, we plan
        # to use them to send alerts too
        self.configure_thresholds()

        # metric select widget
        metric_select = Select(title="Metric:", value=self.selected_metric,
                               options=self.metrics['metrics'], width=100)

        metric_select.on_change("value", self.on_metric_change)

        # data contains values for all the metrics, we load them
        # once and filter by the selected metric
        self.data = {}
        if self.datasets['default']:
            self.data = \
                get_measurements_by_dataset(self.datasets['default'],
                                            len(self.metrics['metrics']))

        self.update_data_source()

        self.make_plot()

        self.layout = row(widgetbox(dataset_select,
                                    metric_select, width=150), self.plot)

    def on_dataset_change(self, attr, old, new):
        """Handle dataset select event, it reloads the measurements
        when another data set is selected and updates the plot

        Parameters
        ----------
        attr : str
            refers to the changed attribute’s name, not used
        old : str
            previous value, not used
        new : str
            new value

        See also
        --------
        http://bokeh.pydata.org/en/latest/docs/user_guide/interaction
        /widgets.html#userguide-interaction-widgets
        """
        self.data = \
            get_measurements_by_dataset(new, len(self.metrics['metrics']))
        self.update_data_source()

    def on_metric_change(self, attr, old, new):
        """Handle metric select event,  it updates the plot when another
         metric is selected using the same data loaded previously

        Parameters
        ----------
        attr : str
            refers to the changed attribute’s name, not used
        old : str
            previous value, not used
        new : str
            new value

        See also
        --------
        http://bokeh.pydata.org/en/latest/docs/user_guide/interaction
        /widgets.html#userguide-interaction-widgets
        """

        # update annotations for the metric thresholds
        for t in self.annotations:
            self.annotations[t]['span'].location =\
                self.thresholds[t]['values'][new]
            self.annotations[t]['label'].y = self.thresholds[t]['values'][new]
            self.annotations[t]['arrow'].y = self.thresholds[t]['values'][new]

        # update plot labels
        self.plot.yaxis.axis_label = new\
            + '(' + self.metrics['units'][new] + ')'

        self.selected_metric = new
        self.update_data_source()

    def update_data_source(self):
        """Update the bokeh data source with measurements for the seleceted
        metric
        """
        # filter measurements by the selected metric
        y = [m['value'] for m in self.data['measurements']
             if m['metric'] == self.selected_metric]

        # all attributes of a datasource must have the same size
        size = len(self.data['dates'])
        units = [self.metrics['units'][self.selected_metric]] * size

        self.source.data = dict(x=self.data['dates'],
                                y=y,
                                desc=self.data['ci_id'],
                                ci_url=self.data['ci_url'],
                                units=units,)

    def make_plot(self):
        """Make the a line-circle-line time series plot with a hover,
        tap and annotations
        """
        # display information associated to each measurement
        hover = HoverTool(tooltips=[("Build ID", "@desc"),
                                    ("Value", "@y (@units)")])

        self.plot = init_time_series_plot(hover=hover)

        line = self.plot.line(
            x='x', y='y', source=self.source,
            line_width=2, color='black',
        )

        self.legends = [("Measurements", [line])]

        self.plot.circle(x='x', y='y', source=self.source,
                         color="black", fill_color="white", size=16,)

        # set a tap tool to link each measurement with the ci_url
        tap = self.plot.select(type=TapTool)
        tap.callback = OpenURL(url="@ci_url")

        # set y-axis label
        self.plot.yaxis.axis_label = self.metrics['default'] +\
            ' (' + self.metrics['units'][self.selected_metric] + ')'

        # make annotations
        self.annotations = {}
        for t in self.thresholds:
            self.annotations[t] = self.make_annotations(self.thresholds[t])

    def make_annotations(self, threshold):
        """Annotate the metric thresholds
        """

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

    def configure_thresholds(self):
        """Thresholds have values for each metric, a text and color
        """

        self.thresholds = {}
        self.thresholds['minimum'] = {'values': self.metrics['minimum'],
                                      'text': 'Minimum Specification',
                                      'color': 'red'}

        self.thresholds['design'] = {'values': self.metrics['design'],
                                     'text': 'Design Specification',
                                     'color': 'blue'}

        self.thresholds['stretch'] = {'values': self.metrics['stretch'],
                                      'text': 'Strecth Goal',
                                      'color': 'green'}


curdoc().add_root(Metrics().layout)
curdoc().title = "SQUASH"
