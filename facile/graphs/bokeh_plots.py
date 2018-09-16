from bokeh import plotting
from bokeh.models import HoverTool
import itertools
import pandas as pd
import numpy as np
from numpy import pi
from bokeh.charts import Bar
from bokeh.charts.attributes import cat, color
from bokeh.charts.operations import blend

colors = itertools.cycle(['#1144cc', '#11cc44', '#cc4411', '#11ccff', '#ff11cc', '#ffcc11', '#111111'])


def plot_series(df, title=None):
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

    fig = plotting.figure(x_axis_type=x_axis_type, title=title, plot_width=700, plot_height=400,
                          tools='', toolbar_location=None, responsive=True)

    for column_name, s in df.iteritems():
        fig.line(list(df.index), s.values, line_width=1.4, color=colors.next(), legend=column_name)

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


def plot_scatter_advanced(df, x, y, color=None, hover=None, title='', plot_width=600, plot_height=600, size=8,
                          l_lines=None):

    if isinstance(df[x].iloc[0], pd.Timestamp):
        x_axis_type = 'datetime'
    else:
        x_axis_type = None

    bokeh_plot = plotting.figure(title=title, width=plot_width, height=plot_height,
                                 x_axis_label=x, y_axis_label=y, x_axis_type=x_axis_type)

    if color is None:
        df['color'] = colors.next()
        color = 'color'

    bokeh_plot.circle(x=x, y=y, color=color, size=size, source=df)

    if hover is not None:
        hover = HoverTool(tooltips=hover)
        bokeh_plot.add_tools(hover)

    if l_lines is not None:
        for line in l_lines:
            bokeh_plot.line(x=line['x'], y=line['y'], line_color=line['color'], line_width=3, legend=line['legend'])

    return bokeh_plot


def plot_pie(df_data, hover=False):

    df_data['angle'] = ((df_data['value'] / df_data.value.sum()) * 2 * pi).cumsum()
    df_data['start_angle'] = [0] + list(df_data['angle'].values[:-1])
    df_data['end_angle'] = ((df_data['value'] / df_data.value.sum()) * 2 * pi).cumsum()
    df_data['color'] = [colors.next() for _ in range(len(df_data))]

    bokeh_plot = plotting.figure(plot_width=700, plot_height=400, tools='', toolbar_location=None, responsive=True)
    for i, row in df_data.iterrows():
        bokeh_plot.annular_wedge(x=[0], y=[0], inner_radius=0.3, outer_radius=0.5, start_angle=[row['start_angle']],
                                 end_angle=[row['end_angle']], color=row['color'], alpha=0.6, legend=[row['name']])

    if hover:
        bokeh_plot.annular_wedge(x=[0] * len(df_data), y=[0] * len(df_data), inner_radius=0.3, outer_radius=0.5,
                                 start_angle=df_data['start_angle'], end_angle=df_data['end_angle'],
                                 color=df_data['color'], alpha=0.0,  source=df_data)

        hover = HoverTool(tooltips="@name: @value")
        bokeh_plot.add_tools(hover)

    # deactivate axis grid and js tools
    bokeh_plot.axis.axis_label = None
    bokeh_plot.axis.visible = False
    bokeh_plot.grid.grid_line_color = None

    return bokeh_plot


def bar_plot(df_data, val_col='value'):
    bar = Bar(df_data,
              values=val_col,
              label=cat(columns='label', sort=False),
              tooltips=[(val_col, '@height')],
              responsive=True, plot_width=700, plot_height=400, tools='', toolbar_location=None, legend=None
              )

    return bar


def stack_bar_plot(df_data, cat_cols):

    bar = Bar(df_data,
              values=blend(*cat_cols, labels_name='cat'),
              label=cat(columns='label', sort=False),
              stack=cat(columns='cat', sort=False),
              color=color(columns='cat', palette=[colors.next() for _ in cat_cols], sort=False),
              tooltips=[('cat', '@cat'), ('value', '@height')],
              responsive=True, plot_width=700, plot_height=400, tools='', toolbar_location=None
              )

    return bar