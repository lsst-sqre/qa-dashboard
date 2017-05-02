import os
import sys
import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Span, Label, Slider
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox

BOKEH_BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(BOKEH_BASE_DIR)

from api_helper import get_url_args, get_data_as_pandas_df # noqa
from bokeh_helper import add_span_annotation # noqa


# Get url query args
args = get_url_args(curdoc, defaults={'metric': 'PA1'})

# Get data
data = get_data_as_pandas_df(endpoint='apps',
                             params=args)

# Configure bokeh data sources with the full and
# selected datasets

snr = {'value': [], 'label': '', 'unit': ''}
selected_snr = []

mag = {'value': [], 'label': '', 'unit': ''}
selected_mag = []

magrms = {'value': [], 'label': '', 'unit': ''}
selected_magrms = []

magerr = {'value': [], 'label': '', 'unit': ''}
selected_magerr = []

if not data.empty:
    snr = data['matchedDataset']['snr']
    mag = data['matchedDataset']['mag']

    # values are in mmag
    magrms = data['matchedDataset']['magrms']
    magerr = data['matchedDataset']['magerr']

    # Selected data based on snr_cut
    index = np.array(snr['value']) > float(args['snr_cut'])

    selected_snr = np.array(snr['value'])[index]
    selected_mag = np.array(mag['value'])[index]
    selected_magrms = np.array(magrms['value'])[index]*1000
    selected_magerr = np.array(magerr['value'])[index]*1000


# TODO: Use astropy quantity for doing these conversions
full = ColumnDataSource(data={'snr': snr['value'], 'mag': mag['value'],
                              'magrms': np.array(magrms['value'])*1000,
                              'magerr': np.array(magerr['value'])*1000})


selected = ColumnDataSource(data={'snr': selected_snr,
                                  'mag': selected_mag,
                                  'magrms': selected_magrms,
                                  'magerr': selected_magerr})
# Configure bokeh widgets

# App title
title = Div(text="""<h2>{metric} diagnostic plot for {ci_dataset} dataset from
                    job ID {ci_id}</h2>""".format_map(args))

# Ranges used in the bokeh widgets
MIN_SNR = 0
MAX_SNR = 500
SNR_STEP = 10

MIN_MAGRMS = 0
MAX_MAGRMS = 50

MIN_DIST = 0
MAX_DIST = 100

# SNR slider
snr_slider = Slider(start=MIN_SNR, end=MAX_SNR,
                    value=float(args['snr_cut']),
                    step=SNR_STEP, title="SNR")

# Scatter plot magrms vs. mag
x_axis_label = "{label} [{unit}]".format_map(mag)


# Plot layout
# | hist, plot1 |
# | plot3, plot2 |

plot1 = figure(tools="pan, box_zoom, wheel_zoom, reset",
               active_scroll="wheel_zoom",
               y_axis_location='right',
               x_axis_label=x_axis_label,
               y_range=(MIN_MAGRMS, MAX_MAGRMS))

scatter1 = plot1.circle('mag', 'magrms', size=5, fill_alpha=0.5,
                        source=full, color='lightgray', line_color=None)

scatter1.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter1 = plot1.circle('mag', 'magrms', size=5, fill_alpha=0.5,
                                source=selected, line_color=None)

partial_scatter1.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=0.5, line_color=None)


# Scatter plot snr vs. mag

x_axis_label = "{label} [{unit}]".format_map(mag)
y_axis_label = "{label}".format_map(snr)

plot2 = figure(tools="pan, box_zoom, wheel_zoom, reset",
               active_scroll="wheel_zoom",
               y_axis_location='right',
               y_axis_label=y_axis_label,
               x_range=plot1.x_range,
               y_range=(MIN_SNR, MAX_SNR),
               x_axis_label=x_axis_label)

scatter2 = plot2.circle('mag', 'snr', size=5, alpha=0.5,
                        source=full, color='lightgray')

scatter2.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter2 = plot2.circle('mag', 'snr', size=5, fill_alpha=0.5,
                                source=selected, line_color=None)

partial_scatter2.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=0.5, line_color=None)
min_snr = 0
if len(selected.data['snr']) > 0:
    min_snr = np.min(selected.data['snr'])


span1 = Span(location=min_snr,
             dimension='width', line_color='black',
             line_dash='dashed', line_width=3)

plot2.add_layout(span1)

# Scatter plot magerr vs. magrms

# TODO: Use astropy quantity for having the right unit here

x_axis_label = "{label} [mmag]".format_map(magrms)
y_axis_label = "{label} [mmag]".format_map(magrms)

plot3 = figure(tools="pan, box_zoom, wheel_zoom, reset",
               active_scroll="wheel_zoom",
               x_axis_label=x_axis_label,
               x_range=plot1.y_range,
               y_axis_label=y_axis_label,
               y_axis_type='log',
               x_axis_type='log')


scatter3 = plot3.circle('magrms', 'magerr', size=5, fill_alpha=0.5,
                        source=full, color='lightgray', line_color=None)

scatter3.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter3 = plot3.circle('magrms', 'magerr', size=5, fill_alpha=0.5,
                                source=selected, line_color=None)

partial_scatter3.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=0.5,
                                             line_color=None)

max_magerr = 0
if len(selected.data['magerr']) > 0:
    max_magerr = np.max(selected.data['magerr'])

span3 = Span(location=max_magerr,
             dimension='width', line_color='black',
             line_dash='dashed', line_width=3)

plot3.add_layout(span3)

min_snr = 0
if len(selected.data['snr']) > 0:
    min_snr = np.min(selected.data['snr'])

label2 = Label(x=200, y=325, x_units='screen', y_units='screen',
               text='SNR > {:3.2f}'.format(min_snr),
               render_mode='css')


plot1.add_layout(label2)

# Full histogram

# TODO: Use astropy quantities for doing this conversion

y_axis_label = "{} [mmag]".format(magrms['label'])

full_hist, edges = np.histogram(full.data['magrms'], bins=100)

hmax = max(full_hist) * 1.1

hist = figure(tools="ypan, ywheel_zoom, reset",
              active_scroll="ywheel_zoom",
              x_range=(0, hmax),
              y_range=plot1.y_range, y_axis_location='left',
              y_axis_label=y_axis_label)

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

add_span_annotation(plot=hist, value=8, text="Minimum", color="red")
add_span_annotation(plot=hist, value=5, text="Design", color="blue")
add_span_annotation(plot=hist, value=3, text="Stretch", color="green")


# Define callbacks
def update(attr, old, new):

    snr_cut = snr_slider.value

    # Update the selected sample
    index = np.array(full.data['snr']) > snr_cut

    tmp = dict(snr=np.array(full.data['snr'])[index],
               mag=np.array(full.data['mag'])[index],
               magrms=np.array(full.data['magrms'])[index],
               magerr=np.array(full.data['magerr'])[index])

    selected.data = tmp

    # Redraw partial histogram
    partial_hist, _ = np.histogram(selected.data['magrms'], bins=edges)
    histogram.data_source.data['right'] = partial_hist

    # Recompute n, median
    n = len(selected.data['magrms'])
    median = np.median(selected.data['magrms'])

    # Update spans

    min_snr = 0
    if len(selected.data['snr']) > 0:
        min_snr = np.min(selected.data['snr'])

    span1.location = min_snr
    span2.location = median

    max_magerr = 0
    if len(selected.data['magerr']) > 0:
        max_magerr = np.max(selected.data['magerr'])

    span3.location = max_magerr

    # Update labels
    label2.text = 'SNR > {:3.2f}'.format(min_snr)
    label3.text = 'Median = {:3.2f} mmag'.format(median)
    label4.text = 'N = {}'.format(n)


snr_slider.on_change('value', update)


# Arrange plots and widgets layout

if data.empty:
    layout = column(widgetbox(title, width=900),
                    widgetbox(Div(text="""<h4>No data to display.</h4>""")))
else:
    layout = row(column(widgetbox(title, width=900),
                        widgetbox(snr_slider, width=900),
                        row(hist, plot1),
                        row(plot3, plot2)))


curdoc().add_root(layout)
curdoc().title = "SQuaSH"
