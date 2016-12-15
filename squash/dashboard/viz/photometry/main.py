import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, TapTool, Span, Label
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox

from dashboard.viz.helper import get_photometry_data, make_title, add_threshold

# App title

title = "Photometry accuracy using {} data set".format("cfht")

description = "{}: " \
              "{}".format("PA1",
                          "The photometric repeatability in the measured"
                          "magnitude of the sources for the same object "
                          "across visits")

title = Div(text=make_title(title=title, description=description))

# Get the data

snr, mag, magrms, magerr, selected_snr, selected_mag, selected_magrms,\
    selected_magerr = get_photometry_data(snr_cut=100)

full = ColumnDataSource(data={'snr': snr, 'mag': mag, 'magrms': magrms,
                              'magerr': magerr})

selected = ColumnDataSource(data={'snr': selected_snr, 'mag': selected_mag,
                                  'magrms': selected_magrms,
                                  'magerr': selected_magerr})

# Configure Bokeh widgets


metric = Div(text="<b>Metric:</b> PA1")

dataset = Div(text="<b>Data Set:</b> cfht")

job = Div(text="<b>Job ID:</b> test")

# Scatter plot mag vs. magrms

plot1 = figure(tools="pan, wheel_zoom, ybox_zoom, tap, reset",
               y_axis_location='right', y_range=(0, 500),
               x_axis_label='r [mag]')

scatter1 = plot1.circle('mag', 'magrms', size=5, alpha=0.5,
                        source=full, color='lightgray')

scatter1.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter1 = plot1.circle('mag', 'magrms', size=5, source=selected)

partial_scatter1.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=1, line_color=None)


# Scatter plot mag  vs. snr

plot2 = figure(toolbar_location=None, y_axis_location='right',
               y_range=(0, 500), y_axis_label='SNR',
               x_range=plot1.x_range, x_axis_label='r [mag]')

scatter2 = plot2.circle('mag', 'snr', size=5, alpha=0.5,
                        source=full, color='lightgray')

scatter2.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter2 = plot2.circle('mag', 'snr', size=5,
                                source=selected)

partial_scatter2.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=1, line_color=None)

span1 = Span(location=np.min(selected.data['snr']),
             dimension='width', line_color='black',
             line_dash='dashed', line_width=3)

plot2.add_layout(span1)

# Scatter plot magrms vs. magerr

plot3 = figure(toolbar_location=None, x_axis_label='RMS [mmag]',
               x_range=plot1.y_range,
               y_axis_label='Median Reported Magnitude err [mmag]',
               y_axis_type='log', x_axis_type='log')

scatter3 = plot3.circle('magrms', 'magerr', size=5, alpha=0.5,
                        source=full, color='lightgray')

scatter3.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter3 = plot3.circle('magrms', 'magerr', size=5,
                                source=selected)

partial_scatter3.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=1, line_color=None)


span3 = Span(location=np.max(selected.data['magerr']),
             dimension='width', line_color='black',
             line_dash='dashed', line_width=3)

plot3.add_layout(span3)

# Capture the click event on the scatter plot

taptool = plot2.select(type=TapTool)

label2 = Label(x=235, y=325, x_units='screen', y_units='screen',
               text='SNR > {:3.2f}'.format(np.min(selected.data['snr'])),
               render_mode='css')

plot1.add_layout(label2)

# Full histogram

full_hist, edges = np.histogram(full.data['magrms'], bins=100)

hmax = max(full_hist) * 1.1

hist = figure(toolbar_location=None, x_range=(0, hmax),
              y_range=plot1.y_range, y_axis_location='left',
              y_axis_label='RMS [mmag]')

hist.ygrid.grid_line_color = None

hist.quad(left=0, bottom=edges[:-1], top=edges[1:], right=full_hist,
          color="lightgray", line_color='lightgray')

# Partial histogram

partial_hist, _ = np.histogram(selected.data['magrms'],
                               bins=edges)

histogram = hist.quad(left=0, bottom=edges[:-1], top=edges[1:],
                      right=partial_hist)

n = len(selected.data['magrms'])

median = np.median(selected.data['magrms'])

# Add annotations to the histograms

label4 = Label(x=200, y=325, x_units='screen', y_units='screen',
               text="N = {}".format(n),
               render_mode='css')

hist.add_layout(label4)

label3 = Label(x=200, y=300, x_units='screen', y_units='screen',
               text="Median = {:3.2f} mmag".format(median),
               render_mode='css')

hist.add_layout(label3)

span2 = Span(location=median,
             dimension='width', line_color="black",
             line_dash='dashed', line_width=3)

hist.add_layout(span2)

add_threshold(plot=hist, value=8, text="Minimum", color="red")
add_threshold(plot=hist, value=5, text="Design", color="blue")
add_threshold(plot=hist, value=3, text="Stretch", color="green")


# Define callbacks
def update(attr, old, new):

    index = new['1d']['indices']

    if len(index) > 0:

        mag_cut = full.data['mag'][index[0]]

        # Update the selected sample
        index = np.array(full.data['mag']) < mag_cut

        selected.data['snr'] = np.array(full.data['snr'])[index]
        selected.data['mag'] = np.array(full.data['mag'])[index]
        selected.data['magrms'] = np.array(full.data['magrms'])[index]
        selected.data['magerr'] = np.array(full.data['magerr'])[index]

        # Redraw partial histogram
        partial_hist, _ = np.histogram(selected.data['magrms'], bins=edges)
        histogram.data_source.data['right'] = partial_hist

        # Recompute n, median
        n = len(selected.data['magrms'])
        median = np.median(selected.data['magrms'])

        # Update spans
        snr_cut = np.min(selected.data['snr'])

        span1.location = snr_cut
        span2.location = median
        span3.location = np.max(selected.data['magerr'])

        # Update labels
        label2.text = 'SNR > {:3.2f}'.format(np.min(selected.data['snr']))
        label3.text = 'Median = {:3.2f} mag'.format(median)
        label4.text = 'N = {}'.format(n)


scatter2.data_source.on_change('selected', update)

# Arrange plots and widgets layout

layout = row(column(widgetbox(metric, width=150),
                    widgetbox(dataset, width=150),
                    widgetbox(job, width=150)),
             column(widgetbox(title, width=1000),
                    row(hist, plot1), row(plot3, plot2)))


curdoc().add_root(layout)
curdoc().title = "SQuaSH"
