from bokeh import plotting
import itertools
import pandas as pd


def plot_series(df, title='bokeh plot'):

    # blue, green, red, cyan, orange, yellow, black
    colors = itertools.cycle(['#1144cc', '#11cc44', '#cc4411', '#11ccff', '#ff11cc', '#ffcc11', '#111111'])

    if isinstance(df.index, pd.DatetimeIndex):
        x_axis_type = 'datetime'
    else:
        x_axis_type = None

    fig = plotting.figure(width=1066, height=600, x_axis_type=x_axis_type, title=title)

    for column_name, s in df.iteritems():
        fig.line(df.index, s.values, line_width=1.4, color=colors.next(), legend=column_name)

    return fig
