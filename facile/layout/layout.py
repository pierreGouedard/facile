from dominate.tags import body, div, p
import dominate
from jinja2 import Template


class Layout(object):

    form_template_variable = '{{form_css}} {{ form_js }} {{ form }}'
    plot_template_variable = '{{ plot_div }} {{ bokeh_js }} {{ bokeh_css }} {{ plot_script }}'
    table_template_variable = ''

    def __init__(self, l_rows, init='doc', title=''):

        self.l_rows = l_rows
        if init == 'doc':
            self.layout = dominate.document(title=title)
        elif init == 'body':
            self.layout = body
        elif init == 'div':
            self.layout = div(id=title)
        else:
            raise ValueError('Init of html document nor understood {}'.format(init))

    def build_template(self):
        with self.layout:
            for name, l_cols in self.l_rows:
                with div(cls='row ', id=name):
                    for d_col in l_cols:
                        with div(cls='col-sm-%i' % d_col['span']):
                            if d_col['content'] == 'form':
                                p(self.form_template_variable)
                            elif d_col['content'] == 'plot':
                                p(self.plot_template_variable)
                            elif d_col['content'] == 'table':
                                p(self.plot_template_variable)


def get_series_layout():
    # Specify rows, columns, there span and content
    l_rows = [('series', [{'span': 3, 'content': 'form'}, {'span': 9, 'content': 'plot'}])]

    # Create layout and build it from l_rows
    layout_series = Layout(l_rows, init='div', title='view_series')
    layout_series.build_template()

    return layout_series.layout.render()


def get_baseline_layout():
    # Specify rows, columns, there span and content
    l_rows = [('baselines', [{'span': 3, 'content': 'form'}, {'span': 9, 'content': 'plot'}])]

    # Create layout and build it from l_rows
    layout_baselines = Layout(l_rows, init='div', title='view_baselines')
    layout_baselines.build_template()

    return layout_baselines.layout.render()


def get_login_layout():

    l_rows = [('login', [{'span': 12, 'content': 'form'}])]

    # Create layout and build it from l_rows
    layout_login = Layout(l_rows, init='div', title='view_series')
    layout_login.build_template()

    return layout_login.layout.render()
