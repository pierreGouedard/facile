from bokeh import plotting
import itertools
import pandas as pd
import numpy as np
colors = itertools.cycle(['#1144cc', '#11cc44', '#cc4411', '#11ccff', '#ff11cc', '#ffcc11', '#111111'])


def plot_series(df, title='bokeh plot'):
    """

    :param df:
    :param title:
    :return:
    """
    if df.empty:
        return

    if isinstance(df.index, pd.DatetimeIndex):
        x_axis_type = 'datetime'
    else:
        x_axis_type = None

    fig = plotting.figure(width=1066, height=600, x_axis_type=x_axis_type, title=title)

    for column_name, s in df.iteritems():
        fig.line(df.index, s.values, line_width=1.4, color=colors.next(), legend=column_name)

    return fig


def plot_series_and_event(df, punctual_event=None, span_event=None, title='bokeh plot'):
    """

    :param df:
    :param punctual_event:
    :param span_event:
    :param title:
    :return:
    """
    if df.empty:
        return

    if isinstance(df.index, pd.DatetimeIndex):
        x_axis_type = 'datetime'
    else:
        x_axis_type = None

    fig = plotting.figure(width=1066, height=600, x_axis_type=x_axis_type, title=title)

    for column_name, s in df.iteritems():
        fig.line(df.index, s.values, line_width=1.4, color=colors.next(), legend=column_name)

    if punctual_event is not None:
        for eid, x_coord in punctual_event.iteritems():
            x, y = [x_coord, x_coord], [min(0, df.sum(axis=1).min()), df.sum(axis=1).max() / (len(df.columns) * 3)]
            fig.line(x=x, y=y, line_color='black', line_width=3, legend='{}: {}'.format('event ID', eid))

    if span_event is not None:
        for column_name, s in span_event.iteritems():
            fig.patch(np.append(s.index, s.index[::-1]), np.append([0] * len(s), s.values[::-1]), color=colors.next(),
                      alpha=0.2, line_color='red', legend=column_name)

    return fig


def plot_scatter(df, x, y, color=None, title='', width=500, height=300):
    from bokeh.charts import Scatter

    # Set color if necessary
    if color is None:
        color = "navy"

    fig = Scatter(df, x=x, y=y, title=title, color=color, width=width, height=height)

    return fig
