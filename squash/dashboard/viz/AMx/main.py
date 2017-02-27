import os
import sys
import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Span, Label, Slider
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(os.path.join(BASE_DIR))

from helper import get_app_data, add_span_annotation, \
                   get_url_args

# URL args and default values for this app

# TODO: defaults should be the same for all apps

args = get_url_args(curdoc, defaults={'metric': 'AM1',
                                      'job__ci_dataset': 'cfht',
                                      'ci_id': 817,
                                      'snr_cut': 100})

# App title
title = Div(text="""<h2>{} diagnostic plot for {} dataset from
                    job ID {}</h2>""".format(args['metric'],
                                             args['job__ci_dataset'],
                                             args['ci_id']))

# Get the data
data = get_app_data(bokeh_app='AMx',
                    ci_id=args['ci_id'],
                    metric=args['metric'],
                    ci_dataset=args['job__ci_dataset'])

# Configure bokeh column data sources
snr = data['matchedDataset']['snr']['value']
dist = data['matchedDataset']['dist']['value']

full = ColumnDataSource(data={'snr': snr, 'dist': dist})

# Selected data based on snr_cut
index = np.array(snr) > float(args['snr_cut'])

selected_snr = np.array(snr)[index]
selected_dist = np.array(dist)[index]

selected = ColumnDataSource(data={'snr': selected_snr, 'dist': selected_dist})

# Configure Bokeh widgets

# SNR slider

snr_slider = Slider(start=0, end=500, value=float(args['snr_cut']), step=1,
                    title="SNR")

# Scatter plot

x_axis_label = data['matchedDataset']['snr']['label']
y_axis_label = "{} [{}]".format(data['matchedDataset']['dist']['label'],
                                data['matchedDataset']['dist']['unit'])

plot = figure(y_range=(0, 500), y_axis_location='left',
              x_axis_label=x_axis_label, x_axis_type='log',
              y_axis_label=y_axis_label)

scatter = plot.circle('snr', 'dist', size=5, fill_alpha=0.2,
                      source=full, color='lightgray',
                      line_color=None)

scatter.nonselection_glyph = Circle(fill_color='lightgray',
                                    line_color=None)

partial_scatter = plot.circle('snr', 'dist', size=5, fill_alpha=0.2,
                              line_color=None, source=selected)

# default bokeh blue color #1f77b4

partial_scatter.nonselection_glyph = Circle(fill_color="#1f77b4",
                                            fill_alpha=0.2,
                                            line_color=None)

# Add annotations to scatter plot

span1 = Span(location=100, dimension='height', line_color='black',
             line_dash='dashed', line_width=3)

plot.add_layout(span1)

label1 = Label(x=285, y=425, x_units='screen', y_units='screen',
               text='SNR > {:3.2f}'.format(span1.location),
               render_mode='css')

plot.add_layout(label1)

# Full histogram

full_hist, edges = np.histogram(full.data['dist'], bins=100)

hmax = max(full_hist) * 1.1

hist = figure(tools="pan, wheel_zoom, ybox_zoom, tap, reset",
              x_range=(0, hmax),
              y_axis_location='right',
              y_range=plot.y_range)

hist.ygrid.grid_line_color = None

hist.quad(left=0, bottom=edges[:-1], top=edges[1:], right=full_hist,
          color="lightgray", line_color='lightgray')

# Partial histogram

partial_hist, _ = np.histogram(selected.data['dist'],
                               bins=edges)

histogram = hist.quad(left=0, bottom=edges[:-1], top=edges[1:],
                      right=partial_hist)

n = len(selected.data['dist'])
median = np.median(selected.data['dist'])
rms = np.sqrt(np.mean(np.square(selected.data['dist'])))

# Add annotations to the histograms

label2 = Label(x=200, y=400, x_units='screen', y_units='screen',
               text='Median = {:3.2f} marcsec'.format(median),
               render_mode='css')

hist.add_layout(label2)

label3 = Label(x=200, y=375, x_units='screen', y_units='screen',
               text='RMS = {:3.2f} marcsec'.format(rms), render_mode='css')

hist.add_layout(label3)

label4 = Label(x=200, y=425, x_units='screen', y_units='screen',
               text='N = {}'.format(n), render_mode='css')

hist.add_layout(label4)

span2 = Span(location=rms,
             dimension='width', line_color="black",
             line_dash='dashed', line_width=3)

hist.add_layout(span2)

add_span_annotation(plot=hist, value=20, text="Minimum", color="red")
add_span_annotation(plot=hist, value=10, text="Design", color="blue")
add_span_annotation(plot=hist, value=5, text="Stretch", color="green")


# Define callbacks
def update(attr, old, new):

    snr_cut = snr_slider.value

    # Update the selected sample
    index = np.array(full.data['snr']) > snr_cut

    selected.data['snr'] = np.array(full.data['snr'])[index]
    selected.data['dist'] = np.array(full.data['dist'])[index]

    # Redraw the partial histogram
    partial_hist, _ = np.histogram(selected.data['dist'],
                                   bins=edges)

    histogram.data_source.data['right'] = partial_hist

    # Recompute n, median and rms
    n = len(selected.data['dist'])
    median = np.median(selected.data['dist'])
    rms = np.sqrt(np.mean(np.square(selected.data['dist'])))

    # Update spans
    span1.location = snr_cut
    span2.location = rms

    # Update labels
    label1.text = 'SNR > {:3.2f}'.format(snr_cut)
    label2.text = 'Median = {:3.2f} marcsec'.format(median)
    label3.text = 'RMS = {:3.2f} marcsec'.format(rms)
    label4.text = 'N = {}'.format(n)


snr_slider.on_change('value', update)

# Arrange plots and widgets layout
layout = row(column(widgetbox(title, width=900),
                    widgetbox(snr_slider, width=900),
                    row(plot, hist)))

curdoc().add_root(layout)
curdoc().title = "SQuaSH"
