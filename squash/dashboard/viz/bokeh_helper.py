from bokeh.models import Span, Label


def add_span_annotation(plot, value, text, color):
    """ Add span annotation, used for metric specification
    thresholds.
    """

    span = Span(location=value, dimension='width',
                line_color=color, line_dash='dotted',
                line_width=2)

    label = Label(x=plot.plot_width-300, y=value+0.5, x_units='screen',
                  y_units='data', text=text, text_color=color,
                  text_font_size='11pt', text_font_style='normal',
                  render_mode='canvas')

    plot.add_layout(span)
    plot.add_layout(label)
