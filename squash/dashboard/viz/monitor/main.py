import os
import sys
import time
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, Span, Label,\
    BoxAnnotation
from bokeh.models.widgets import Select, Div, DataTable, TableColumn,\
    HTMLTemplateFormatter
from bokeh.layouts import row, widgetbox, column
from defaults import init_time_series_plot

SQUASH_BASE_URL = os.environ.get('SQUASH_BASE_URL',
                                 'http://localhost:8000')

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(os.path.join(BASE_DIR))

from api_helper import get_datasets, get_metrics, get_specs, \
                   get_meas_by_dataset_and_metric, get_url_args # noqa


class Metrics(object):
    """The metrics app consists of a time series plot showing measurements
    for a given selected dataset and metric.
    """

    def __init__(self):

        # app title
        self.title = Div(text="")

        # data contains values for the selected dataset and metric
        self.data = {}

        # this column data source is used by bokeh to update the plot
        self.source = ColumnDataSource(data={'x': [], 'y': [], 'time': [],
                                             'ci_ids': [],
                                             'ci_urls': [], 'units': [],
                                             'names': [], 'git_urls': [],
                                             })

        self.compose_layout()

    def compose_layout(self):
        """Compose the layout ot the app, the main elements are the widgets to
        select the dataset, the metric, a div for the title, a plot and a table
        """

        # Load metrics and datasets
        self.metrics = get_metrics(default='AM1')
        self.datasets = get_datasets(default='cfht')

        # Get args from the app URL or use defaults
        args = get_url_args(doc=curdoc,
                            defaults={'metric': self.metrics['default']})

        self.selected_dataset = args['job__ci_dataset']

        self.selected_metric = args['metric']

        # get specifications for the selected metric
        self.specs = get_specs(self.selected_metric)

        self.selected_window = args['window']

        # dataset select widget
        dataset_select = Select(title="Data Set:",
                                value=self.selected_dataset,
                                options=self.datasets['datasets'], width=100)

        dataset_select.on_change("value", self.on_dataset_change)

        # thresholds are used to make plot annotations
        self.configure_thresholds()

        # metric select widget
        metric_select = Select(title="Metric:", value=self.selected_metric,
                               options=self.metrics['metrics'], width=100)

        metric_select.on_change("value", self.on_metric_change)

        self.data = \
            get_meas_by_dataset_and_metric(self.selected_dataset,
                                           self.selected_metric,
                                           self.selected_window)

        self.update_data_source()
        self.make_plot()
        self.make_table()

        if len(self.data['values']) < 1:
            self.loading.text = "No data to display"
        else:
            self.loading.text = ""

        self.layout = row(widgetbox(dataset_select,
                                    metric_select,
                                    width=150),
                          column(widgetbox(self.title, width=1000),
                                 self.plot,
                                 widgetbox(self.table_title, width=1000),
                                 self.table))

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

        self.loading.text = "Loading..."

        self.data = \
            get_meas_by_dataset_and_metric(new, self.selected_metric,
                                           self.selected_window)

        self.selected_dataset = new

        self.update_data_source()

        # Update data table columns, the link to the diagnostic bokeh apps
        # depends on the selected dataset

        self.table.columns = self.update_table_columns()

        if len(self.data['values']) < 2:
            self.loading.text = "No data to display"
        else:
            self.loading.text = ""

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

        self.loading.text = "Loading..."
        self.selected_metric = new
        self.configure_thresholds()

        # update annotations for the metric thresholds
        for t in self.annotations:
            self.annotations[t]['span'].location =\
                self.thresholds[t]['values']
            self.annotations[t]['label'].y = self.thresholds[t]['values']

        # update specs
        self.specs = get_specs(self.selected_metric)

        self.data = \
            get_meas_by_dataset_and_metric(self.selected_dataset, new,
                                           self.selected_window)
        # update plot labels
        self.plot.yaxis.axis_label = "{} [{}]".format(new,
                                                      self.specs['unit'])

        self.update_data_source()

        if len(self.data['values']) < 1:
            self.loading.text = "No data to display"
        else:
            self.loading.text = ""

        # Update data table columns, the link to the diagnostic bokeh apps
        # depends on the selected metric

        self.table.columns = self.update_table_columns()

    def update_data_source(self):
        """Update the bokeh data source with measurements for the selected
        dataset and metric
        """

        # plot title and description must be updated each time
        # the dataset and metric changes

        title = "{} measurements for {} dataset".format(self.selected_metric,
                                                        self.selected_dataset)
        description = self.specs['description']

        self.title.text = self.make_title(title, description)

        # all attributes of a datasource must have the same size
        size = len(self.data['dates'])
        units = [self.specs['unit']] * size

        self.source.data = dict(x=self.data['dates'],
                                y=self.data['values'],
                                time=[x.strftime("%Y-%m-%d %H:%M:%S")
                                      for x in self.data['dates']],
                                ci_ids=self.data['ci_ids'],
                                ci_urls=self.data['ci_urls'],
                                units=units,
                                names=self.data['names'],
                                git_urls=self.data['git_urls'])

    def make_title(self, title, description=""):
        """ Update page title with the selected metric
        """
        return """<left><h2>{}</h2>{}
        </left>""".format(title, description)

    def make_plot(self):
        """Make the a line-circle-line time series plot with a hover,
        tap and annotations
        """

        # display information associated to each measurement
        hover = HoverTool(tooltips=[("Time", "@time"),
                                    ("Value", "@y (@units)"),
                                    ("Job ID", "@ci_ids")])

        self.plot = init_time_series_plot(hover=hover)

        self.loading = Label(x=350,
                             y=200,
                             x_units='screen',
                             y_units='screen',
                             text="Loading...",
                             text_color="lightgray",
                             text_font_size='36pt',
                             text_font_style='normal')

        self.plot.add_layout(self.loading)

        self.plot.line(
            x='x', y='y', source=self.source,
            line_width=2, color='black')

        self.plot.circle(x='x', y='y', source=self.source,
                                  color="black", fill_color="white", size=16,)

        # set y-axis label
        self.plot.yaxis.axis_label = "{} [{}]".format(self.metrics['default'],
                                                      self.specs['unit'])

        # make annotations
        self.annotations = {}
        for t in self.thresholds:
            self.annotations[t] = self.make_annotations(self.thresholds[t])

        # box annotations are created once for the default metric and are
        # not update
        self.make_box_annotations()

    def update_table_columns(self):
        """Format links used in data table"""

        # Name convention for diagnostic bokeh apps, e.g. the bokeh app for
        # displaying diagnostic plots for metrics AM1, AM2, AM3 is named AMx

        bokeh_app = self.selected_metric.replace(self.selected_metric[-1], 'x')
        bokeh_app_url = "{}/dashboard/{}".format(SQUASH_BASE_URL, bokeh_app)

        # job id is selected from the table
        params = "?metric={}&" \
                 "job__ci_dataset={}&" \
                 "ci_id=<%= ci_ids %>".format(self.selected_metric,
                                              self.selected_dataset)

        bokeh_app_url = "{}/{}".format(bokeh_app_url, params)

        template = '<a href="{}"><%= value %></a>'.format(bokeh_app_url)
        value_url_formatter = HTMLTemplateFormatter(template=template)

        template = '<a href="<%= ci_urls %>"><%= value %></a>'
        ci_url_formatter = HTMLTemplateFormatter(template=template)

        template = '<% for (x in git_urls) { ' \
                   '       if (x>0) print(", "); ' \
                   '       print("<a href=" + git_urls[x] + ">" ' \
                   '              + value[x] + "</a>")' \
                   '   }; ' \
                   '%>'
        git_url_formatter = HTMLTemplateFormatter(template=template)

        columns = [
            TableColumn(field="time", title="Time",
                        width=200),
            TableColumn(field="ci_ids", title="Job ID",
                        formatter=ci_url_formatter, width=100),
            TableColumn(field="y", title="Value",
                        formatter=value_url_formatter,
                        width=100, sortable=False),
            TableColumn(field="names", title="Packages",
                        formatter=git_url_formatter, width=600,
                        sortable=False),
        ]

        return columns

    def make_table(self):
        """Make a data table to list the packages that changed with respect to
        the previous build, add links to diagnostic plots associated with
        measurement values and to the corresponding Jenkins Job and git URLs
        """
        title = "Code Changes"

        description = "The table lists measurements values for each job " \
                      "and packages that have changed with respect "\
                      "to the pevious job." \
                      " Tap on the job ID, on the values or on the package" \
                      " names for more information."

        self.table_title = Div(text=self.make_title(title, description))

        columns = self.update_table_columns()

        self.table = DataTable(
            source=self.source, columns=columns, width=1000, height=200,
            row_headers=True, fit_columns=False, scroll_to_selection=True,
            editable=False
        )

    def make_annotations(self, threshold):
        """Annotate the metric thresholds
        """

        location = threshold['values']
        color = threshold['color']

        span = Span(location=location, dimension='width',
                    line_width=2, line_color=color, line_dash='dotted',)

        self.plot.add_layout(span)

        text = threshold['text']

        label = Label(x=70, y=location, x_units='screen',
                      y_units='data', text=text, text_color=color,
                      text_font_size='11pt', text_font_style='normal')

        self.plot.add_layout(label)

        return {'span': span, 'label': label}

    def get_box_coords(self):
        """Get coords used in box annotation
        """

        last = len(self.data['ci_ids']) - 2
        start = []
        end = []

        for i, current in enumerate(self.data['ci_ids']):
            if i < last:
                next = self.data['ci_ids'][i+1]
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
        """Box annotations indicate regions in the plot with missing jobs
        looking at missing values in the ci_ids list
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
        self.thresholds['minimum'] = {'values': self.specs['minimum'],
                                      'text': 'Minimum',
                                      'color': 'red'}

        self.thresholds['design'] = {'values': self.specs['design'],
                                     'text': 'Design',
                                     'color': 'blue'}

        self.thresholds['stretch'] = {'values': self.specs['stretch'],
                                      'text': 'Stretch',
                                      'color': 'green'}


curdoc().add_root(Metrics().layout)
curdoc().title = "SQUASH"
