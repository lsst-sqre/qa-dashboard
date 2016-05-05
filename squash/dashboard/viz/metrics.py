from datetime import datetime
from bokeh.models import HoverTool
from bokeh.models import ColumnDataSource
from .defaults import init_time_series_plot, init_legend


def update_metric_data(user, session):
    pass


def make_metric_plot(user):
    legends = []

    # Hardcoded values to test bokeh plot
    metric = "PA1"
    unit = "mag"
    runtime = [datetime(2016, 5, 2), datetime(2016, 5, 3),
               datetime(2016, 5, 4), datetime(2016, 5, 5)]
    measurements = [1.5, 2.5, 2, 2.5, 2]
    builds = [123, 124, 125, 126, 127]

    source = ColumnDataSource(
            data=dict(x=runtime, y=measurements, desc=builds),
        )

    hover = HoverTool(tooltips=[("Build", "@desc"), (metric, "@y "+unit)])

    plot = init_time_series_plot(hover=hover)

    line = plot.line(
            x='x', y='y', source=source,
            line_width=2, line_cap='round'
        )

    plot.circle(x='x', y='y', source=source, fill_color="white", size=16)

    plot.yaxis.axis_label = metric + '(' + unit + ')'

    legends.append((metric, [line]))
    plot.add_layout(init_legend(legends=legends))
    return plot
