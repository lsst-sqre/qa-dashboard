import time
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, OpenURL, TapTool, HoverTool,\
                         Span, Label, BoxAnnotation
from bokeh.models.widgets import Select, Div
from bokeh.layouts import row, widgetbox, column
from defaults import init_time_series_plot
from service import get_datasets, get_metrics, get_measurements_by_dataset


class Metrics(object):
    """The metrics app consists of a time series plot showing measurements
    for a given selected dataset and metric.
    """

    def __init__(self):

        self.source = ColumnDataSource(data={'x': [], 'y': [], 'desc': [],
                                             'ci_url': [], 'units': []})
        self.compose_layout()

    def compose_layout(self):
        """Compose the layout ot the app, the main elements are the widgets to
        select the dataset, the metric, a div for the title and the plot
        """
        self.datasets = get_datasets()
        self.selected_dataset = self.datasets['default']

        # dataset select widget
        dataset_select = Select(title="Data Set:",
                                value=self.selected_dataset,
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
        self.title = Div(text=self.make_title())
        self.make_plot()

        self.layout = row(widgetbox(dataset_select, metric_select, width=150),
                          column(widgetbox(self.title, width=1000), self.plot))

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

        self.selected_dataset = new
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

        # update plot labels
        self.plot.yaxis.axis_label = new\
            + '(' + self.metrics['units'][new] + ')'

        self.selected_metric = new
        self.title.text = self.make_title()
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

    def make_title(self):
        """ Update page title with the selected metric
        """
        text = """<center><h4>{}</h4>{}
        </center>""".format(self.selected_metric,
                            self.metrics['description'][self.selected_metric])
        return text

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

        self.box_annotations = self.make_box_annotations()

    def make_annotations(self, threshold):
        """Annotate the metric thresholds
        """

        location = threshold['values'][self.selected_metric]
        color = threshold['color']

        span = Span(location=location, dimension='width',
                    line_width=2, line_color=color, line_dash='dotted',)

        self.plot.add_layout(span)

        text = threshold['text']

        label = Label(x=70, y=location, x_units='screen',
                      y_units='data', text=text + " &darr;", text_color=color,
                      text_font_size='11pt', text_font_style='normal',
                      render_mode='css')

        self.plot.add_layout(label)

        return {'span': span, 'label': label}

    def get_box_coords(self):

        last = len(self.data['ci_id']) - 2

        start = []
        end = []

        for i, current in enumerate(self.data['ci_id']):
            if i < last:
                next = self.data['ci_id'][i+i]
                if (next - current) > 1:
                    start.append(time.mktime(
                        self.data['dates'][i].timetuple())*1000)
                    end.append(time.mktime(
                        self.data['dates'][i+1].timetuple())*1000)
                else:
                    start.append(time.mktime(
                        self.data['dates'][i].timetuple())*1000)
                    end.append(time.mktime(
                        self.data['dates'][i].timetuple())*1000)

        return zip(start, end)

    def make_box_annotations(self):
        """Box annotations indicate regions in the plot with failed jobs
        """
        box = []
        coords = self.get_box_coords()

        for l, r in coords:
            b = BoxAnnotation(left=l, right=r, fill_alpha=0.1,
                              fill_color='red')
            self.plot.add_layout(b)
            box.append(b)

        return box

    def configure_thresholds(self):
        """Thresholds have values for each metric, a text and color
        """
        self.thresholds = {}
        self.thresholds['minimum'] = {'values': self.metrics['minimum'],
                                      'text': 'Minimum',
                                      'color': 'red'}

        self.thresholds['design'] = {'values': self.metrics['design'],
                                     'text': 'Design',
                                     'color': 'blue'}

        self.thresholds['stretch'] = {'values': self.metrics['stretch'],
                                      'text': 'Stretch',
                                      'color': 'green'}


curdoc().add_root(Metrics().layout)
curdoc().title = "SQUASH"
