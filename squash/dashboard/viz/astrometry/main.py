import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, TapTool, Span, Select, Label
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox

from dashboard.viz.helper import get_astrometry_data, make_title, add_threshold

# App title

title = "Relative astrometry using {} data set".format("cfht")

description = "{}: " \
              "{}".format("AM1",
                          "The RMS of the astrometric distance distribution "
                          "for stellar pairs with separation of 5 arcmin "
                          "(repeatability)")

title = Div(text=make_title(title=title, description=description))

# Get the data

snr, dist, selected_snr, selected_dist = get_astrometry_data(snr_cut=100)

full = ColumnDataSource(data={'snr': snr, 'dist': dist})

selected = ColumnDataSource(data={'snr': selected_snr, 'dist': selected_dist})

# Configure Bokeh widgets

metric = Select(title="Metric:",
                options=['AM1'],
                value='AM1')

dataset = Select(title="Data Set:",
                 options=['cfht'],
                 value='cfht')

# Scatter plot

plot = figure(tools="pan, wheel_zoom, ybox_zoom, tap, reset",
              y_axis_location='right', y_range=(0, 500),
              x_axis_label='SNR', x_axis_type='log')

scatter = plot.circle('snr', 'dist', size=5, alpha=0.5, source=full,
                      color='lightgray')

scatter.nonselection_glyph = Circle(fill_color='lightgray', line_color=None)

partial_scatter = plot.circle('snr', 'dist', size=5, source=selected)

partial_scatter.nonselection_glyph = Circle(fill_color="#1f77b4", fill_alpha=1,
                                            line_color=None)

# Capture the click event on the scatter plot

taptool = plot.select(type=TapTool)

# Add annotations to scatter plot

span1 = Span(location=100, dimension='height', line_color='black',
             line_dash='dashed', line_width=3)

plot.add_layout(span1)

label1 = Label(x=285, y=400, x_units='screen', y_units='screen',
               text='SNR > {:3.2f}'.format(span1.location),
               render_mode='css')

plot.add_layout(label1)

# Full histogram

full_hist, edges = np.histogram(full.data['dist'], bins=100)

hmax = max(full_hist) * 1.1

hist = figure(toolbar_location=None, x_range=(0, hmax),
              y_range=plot.y_range, y_axis_location='left',
              y_axis_label='Distance [masrsec]')

hist.ygrid.grid_line_color = None

hist.quad(left=0, bottom=edges[:-1], top=edges[1:], right=full_hist,
          color="lightgray", line_color='lightgray')

# Partial histogram

partial_hist, _ = np.histogram(selected.data['dist'],
                               bins=edges)

histogram = hist.quad(left=0, bottom=edges[:-1], top=edges[1:],
                      right=partial_hist)

median = np.median(selected.data['dist'])

rms = np.sqrt(np.mean(np.square(selected.data['dist'])))

# Add annotations to the histograms

label2 = Label(x=250, y=400, x_units='screen', y_units='screen',
               text='Median = {:3.2f} marcsec'.format(median),
               render_mode='css')

hist.add_layout(label2)

label3 = Label(x=250, y=380, x_units='screen', y_units='screen',
               text='RMS = {:3.2f} marcsec'.format(rms), render_mode='css')

hist.add_layout(label3)

span2 = Span(location=rms,
             dimension='width', line_color="black",
             line_dash='dashed', line_width=3)

hist.add_layout(span2)

add_threshold(plot=hist, value=20, text="Minimum", color="red")
add_threshold(plot=hist, value=10, text="Design", color="blue")
add_threshold(plot=hist, value=5, text="Stretch", color="green")


# Define callbacks
def update(attr, old, new):

    index = new['1d']['indices']

    if len(index) > 0:

        snr_cut = full.data['snr'][index[0]]

        # Update the selected sample
        index = np.array(full.data['snr']) > snr_cut

        selected.data['dist'] = np.array(full.data['dist'])[index]
        selected.data['snr'] = np.array(full.data['snr'])[index]

        # Redraw partial histogram
        partial_hist, _ = np.histogram(selected.data['dist'],
                                       bins=edges)
        histogram.data_source.data['right'] = partial_hist

        # Recompute median and rms
        median = np.median(selected.data['dist'])
        rms = np.sqrt(np.mean(np.square(selected.data['dist'])))

        # Update spans
        span1.location = snr_cut
        span2.location = rms

        # Update labels
        label1.text = 'SNR > {:3.2f}'.format(snr_cut)
        label2.text = 'Median = {:3.2f} marcsec'.format(median)
        label3.text = 'RMS = {:3.2f} marcsec'.format(rms)


scatter.data_source.on_change('selected', update)

# Arrange plots and widgets layout

layout = row(column(widgetbox(metric, width=150),
                    widgetbox(dataset, width=150)),
             column(widgetbox(title, width=900),
                    row(hist, plot)))

curdoc().add_root(layout)
curdoc().title = "SQuaSH"
