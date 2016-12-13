import time
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool,\
                         Span, Label, BoxAnnotation
from bokeh.models.widgets import Select, Div, DataTable, TableColumn,\
                                 DateFormatter, HTMLTemplateFormatter
from bokeh.layouts import row, widgetbox, column
from defaults import init_time_series_plot

from dashboard.viz.helper import get_datasets, get_metrics,\
                                 get_meas_by_dataset_and_metric


class Regression(object):
    """The regression app consists of a time series plot showing measurements
    for a given selected dataset and metric linked to a data table listing
    code changes
    """

    def __init__(self):

        # app title
        self.title = Div(text="")

        # data contains values for the selected dataset and metric
        self.data = {}

        # this column data source is used by bokeh to update the plot
        self.source = ColumnDataSource(data={'x': [], 'y': [], 'ci_ids': [],
                                             'ci_urls': [], 'units': [],
                                             'names': [], 'git_urls': [],
                                             })

        self.compose_layout()

    def compose_layout(self):
        """Compose the layout ot the app, the main elements are the widgets to
        select the dataset, the metric, a div for the title, a plot and a table
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

        # thresholds are used to make plot annotations
        self.configure_thresholds()

        # metric select widget
        metric_select = Select(title="Metric:", value=self.selected_metric,
                               options=self.metrics['metrics'], width=100)

        metric_select.on_change("value", self.on_metric_change)

        self.data = \
            get_meas_by_dataset_and_metric(self.selected_dataset,
                                           self.selected_metric)
        self.update_data_source()

        self.make_plot()

        title = "Code Changes"

        description = "The table lists the metric measurements for each job " \
                      "and the packages that have changed with respect "\
                      "to the pevious job." \
                      "Tap on the Job ID or on the Package name for more " \
                      "information."

        table_title = Div(text=self.make_title(title, description))

        self.make_table()

        self.layout = row(widgetbox(metric_select, dataset_select, width=150),
                          column(widgetbox(self.title, width=1000),
                                 self.plot,
                                 widgetbox(table_title, width=1000),
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

        self.data = \
            get_meas_by_dataset_and_metric(new, self.selected_metric)

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

        self.data = \
            get_meas_by_dataset_and_metric(self.selected_dataset, new)

        self.update_data_source()

    def update_data_source(self):
        """Update the bokeh data source with measurements for the selected
        dataset and metric
        """

        # all attributes of a datasource must have the same size
        size = len(self.data['dates'])
        units = [self.metrics['units'][self.selected_metric]] * size

        self.source.data = dict(x=self.data['dates'],
                                y=self.data['values'],
                                ci_ids=self.data['ci_ids'],
                                ci_urls=self.data['ci_urls'],
                                units=units,
                                names=self.data['names'],
                                git_urls=self.data['git_urls'])

        # plot title and description must be updated each time
        # the dataset and metric changes

        title = "Testing {} regression " \
                "using {} data set".format(self.selected_metric,
                                           self.selected_dataset)

        description = "{}: " \
                      "{}".format(self.selected_metric,
                                  self.metrics['description'][self.selected_metric])

        self.title.text = self.make_title(title, description)

    def make_title(self, title, description):
        """ Update page title with the selected metric
        """

        return """<left><h2>{}</h2>{}
        </left>""".format(title, description)

    def make_plot(self):
        """Make the a line-circle-line time series plot with a hover,
        tap and annotations
        """

        # display information associated to each measurement
        hover = HoverTool(tooltips=[("Job ID", "@ci_ids"),
                                    ("Value", "@y (@units)")])

        self.plot = init_time_series_plot(hover=hover)

        line = self.plot.line(
            x='x', y='y', source=self.source,
            line_width=2, color='black')

        self.legends = [("Measurements", [line])]

        self.plot.circle(x='x', y='y', source=self.source,
                         color="black", fill_color="white", size=16,)

        # set y-axis label
        self.plot.yaxis.axis_label = self.metrics['default'] +\
            ' [' + self.metrics['units'][self.selected_metric] + ']'

        # make annotations
        self.annotations = {}
        for t in self.thresholds:
            self.annotations[t] = self.make_annotations(self.thresholds[t])

        self.box_annotations = self.make_box_annotations()

    def make_table(self):
        """Make a data table to list the packages that changed with respect to
        the previous build
        """

        x_formatter = DateFormatter(format="m/d/y")

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
            TableColumn(field="x", title="Date",
                        formatter=x_formatter, width=100),
            TableColumn(field="ci_ids", title="Job ID",
                        formatter=ci_url_formatter, width=100),
            TableColumn(field="y", title="Value", width=100,
                        sortable=False),
            TableColumn(field="names", title="Packages",
                        formatter=git_url_formatter, width=600,
                        sortable=False),
        ]

        self.table = DataTable(
            source=self.source, columns=columns, width=900, height=200,
            row_headers=True, fit_columns=False, scroll_to_selection=True,
            editable=False
        )

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
                      y_units='data', text=text, text_color=color,
                      text_font_size='11pt', text_font_style='normal',
                      render_mode='canvas')

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
        self.thresholds['minimum'] = {'values': self.metrics['minimum'],
                                      'text': 'Minimum',
                                      'color': 'red'}

        self.thresholds['design'] = {'values': self.metrics['design'],
                                     'text': 'Design',
                                     'color': 'blue'}

        self.thresholds['stretch'] = {'values': self.metrics['stretch'],
                                      'text': 'Stretch',
                                      'color': 'green'}


curdoc().add_root(Regression().layout)
curdoc().title = "SQuaSH"
