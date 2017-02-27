import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Span, Label, Slider
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Circle
from bokeh.plotting import figure
from bokeh.layouts import row, column, widgetbox

from dashboard.viz.helper import get_app_data, \
    add_span_annotation, \
    get_url_args


# TODO: defaults should be the same for all apps

args = get_url_args(curdoc, defaults={'metric': 'PA1',
                                      'job__ci_dataset': 'cfht',
                                      'ci_id': 817,
                                      'snr_cut': 100})
# App title
title = Div(text="""<h2>{} diagnostic plot for {} dataset
                    from job ID {}</h2>""".format(args['metric'],
                                                  args['job__ci_dataset'],
                                                  args['ci_id']))

data = get_app_data(bokeh_app='PAx',
                    ci_id=args['ci_id'],
                    metric=args['metric'],
                    ci_dataset=args['job__ci_dataset'])

# Get the data
snr = data['matchedDataset']['snr']['value']
mag = data['matchedDataset']['mag']['value']

# TODO: use astropy quantity for doing these conversions
magrms = np.array(data['matchedDataset']['magrms']['value'])*1000
magerr = np.array(data['matchedDataset']['magerr']['value'])*1000

# Configure bokeh column data sources
full = ColumnDataSource(data={'snr': snr, 'mag': mag, 'magrms': magrms,
                              'magerr': magerr})


# Selected data based on snr_cut
index = np.array(snr) > float(args['snr_cut'])

selected_snr = np.array(snr)[index]
selected_mag = np.array(mag)[index]
selected_magrms = np.array(magrms)[index]
selected_magerr = np.array(magerr)[index]

selected = ColumnDataSource(data={'snr': selected_snr,
                                  'mag': selected_mag,
                                  'magrms': selected_magrms,
                                  'magerr': selected_magerr})

# SNR slider
snr_slider = Slider(start=0, end=500,
                    value=float(args['snr_cut']),
                    step=1, title="SNR")

# Scatter plot magrms vs. mag

x_axis_label = "{} [{}]".format(data['matchedDataset']['mag']['label'],
                                data['matchedDataset']['mag']['unit'])


# Plot layout
# | hist, plot1 |
# | plot3, plot2 |

plot1 = figure(tools="pan, wheel_zoom, ybox_zoom, tap, reset",
               y_axis_location='right',
               x_axis_label=x_axis_label,
               y_range=(0, 500))

scatter1 = plot1.circle('mag', 'magrms', size=5, fill_alpha=0.5,
                        source=full, color='lightgray', line_color=None)

scatter1.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter1 = plot1.circle('mag', 'magrms', size=5, fill_alpha=0.5,
                                source=selected, line_color=None)

partial_scatter1.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=0.5, line_color=None)


# Scatter plot snr vs. mag

x_axis_label = "{} [{}]".format(data['matchedDataset']['mag']['label'],
                                data['matchedDataset']['mag']['unit'])

y_axis_label = data['matchedDataset']['snr']['label']

plot2 = figure(tools="pan, wheel_zoom, box_zoom, reset",
               y_axis_location='right',
               y_axis_label=y_axis_label,
               x_range=plot1.x_range,
               y_range=(0, 500),
               x_axis_label=x_axis_label)

scatter2 = plot2.circle('mag', 'snr', size=5, alpha=0.5,
                        source=full, color='lightgray')

scatter2.nonselection_glyph = Circle(fill_color='lightgray',
                                     line_color=None)

partial_scatter2 = plot2.circle('mag', 'snr', size=5, fill_alpha=0.5,
                                source=selected, line_color=None)

partial_scatter2.nonselection_glyph = Circle(fill_color="#1f77b4",
                                             fill_alpha=0.5, line_color=None)

span1 = Span(location=np.min(selected.data['snr']),
             dimension='width', line_color='black',
             line_dash='dashed', line_width=3)

plot2.add_layout(span1)

# Scatter plot magerr vs. magrms

# TODO: Use astropy quantities for doing these conversions

x_axis_label = "{} [mmag]".format(data['matchedDataset']['magrms']['label'])
y_axis_label = "{} [mmag]".format(data['matchedDataset']['magerr']['label'])

plot3 = figure(tools="pan, wheel_zoom, box_zoom, reset",
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


span3 = Span(location=np.max(selected.data['magerr']),
             dimension='width', line_color='black',
             line_dash='dashed', line_width=3)

plot3.add_layout(span3)

label2 = Label(x=200, y=325, x_units='screen', y_units='screen',
               text='SNR > {:3.2f}'.format(np.min(selected.data['snr'])),
               render_mode='css')

plot1.add_layout(label2)

# Full histogram

# TODO: Use astropy quantities for doing this conversion

y_axis_label = "{} [mmag]".format(data['matchedDataset']['magrms']['label'])

full_hist, edges = np.histogram(full.data['magrms'], bins=100)

hmax = max(full_hist) * 1.1

hist = figure(tools="pan, wheel_zoom, ybox_zoom, reset", x_range=(0, hmax),
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
    label3.text = 'Median = {:3.2f} mmag'.format(median)
    label4.text = 'N = {}'.format(n)


snr_slider.on_change('value', update)

# Arrange plots and widgets layout
layout = row(column(widgetbox(title, width=900),
                    widgetbox(snr_slider, width=900),
                    row(hist, plot1),
                    row(plot3, plot2)))


curdoc().add_root(layout)
curdoc().title = "SQuaSH"
