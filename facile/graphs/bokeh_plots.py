from bokeh import plotting
import itertools
import pandas as pd

colors = itertools.cycle(['#1144cc', '#11cc44', '#cc4411', '#11ccff', '#ff11cc', '#ffcc11', '#111111'])


def plot_series(df, title='bokeh plot'):

    if isinstance(df.index, pd.DatetimeIndex):
        x_axis_type = 'datetime'
    else:
        x_axis_type = None

    fig = plotting.figure(width=1066, height=600, x_axis_type=x_axis_type, title=title)

    for column_name, s in df.iteritems():
        fig.line(df.index, s.values, line_width=1.4, color=colors.next(), legend=column_name)

    return fig


def plot_series_and_event(df, s_spots, title='bokeh plot'):

    if isinstance(df.index, pd.DatetimeIndex):
        x_axis_type = 'datetime'
    else:
        x_axis_type = None

    fig = plotting.figure(width=1066, height=600, x_axis_type=x_axis_type, title=title)

    for column_name, s in df.iteritems():
        fig.line(df.index, s.values, line_width=1.4, color=colors.next(), legend=column_name)

    l_vline, name = [], s_spots.name
    for sid, rat in s_spots.iteritems():
        x, y = [rat, rat], [min(0, df.sum(axis=1).min()), df.sum(axis=1).max() / (len(df.columns) * 3)]
        fig.line(x=x, y=y, line_color='black', line_width=3, legend='{}: {}'.format(name, sid))

    fig.renderers.extend(l_vline)

    return fig
