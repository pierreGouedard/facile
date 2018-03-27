from dominate.tags import body, div, p, table, col, thead, tr, th, tbody, td
import dominate
from jinja2 import Template
import os
from flask import render_template_string, url_for


class Table(object):
    css_static = '<link rel="stylesheet" type="text/css" href="%s"></link>'
    js_static = '<script type="text/javascript" src="%s"></script>'
    template_static = os.path.join(url_for('static'), 'template/%s')
    href = "{{url_for('static', filename='table/%s')}}"

    def __init__(self, column_names, is_index=True, index_name=None, fixed_header=True, fixed_index=False,
                 d_sizes=None):

        self.column_names = column_names
        self.is_index = is_index
        self.index_name = []
        if is_index:
            self.index_name = [index_name] if index_name is not None else 'Index'


        self.fixed_header = fixed_header

        if not fixed_header and fixed_index:
            self.fixed_index = True
        else:
            self.fixed_index = False

        if d_sizes is not None:
            self.l_sizes = [(name, '200px') for name in self.column_names + [self.index_name]]
        else:
            self.l_sizes = [(name, d_sizes.get(name, "200px")) for name in self.column_names + [self.index_name]]

    def get_table_resources(self):
        ressource = {'template': self.template_static % 'fixedheader.html',
                     'css': [self.css_static % self.href % 'css/mainfixedheader.css',
                             self.css_static % self.href % 'css/perfect-scrollbar.css'],
                     'js': [self.js_static % self.href % 'js/perfect-scrollbar.min.js']
                     }

        if self.fixed_index:
            ressource.update({'template': self.template_static % 'fixedcolumn.html',
                              'css': [self.css_static % self.href % 'css/mainfixedcolumn.css',
                                      self.css_static % self.href % 'css/perfect-scrollbar.css']
                              })

    def render_table_from_pandas(self, df):

        # Fixed Head !!!!!
        html_head = table
        with html_head:
            for c, s in self.l_sizes:
                col(width=s)
            with thead:
                with tr(cls="row100 head"):
                    for c, _ in self.l_sizes:
                        th(c, cls="cell100 column")

        html_body = table
        with html_body:
            for c, s in self.l_sizes:
                col(width=s)
            with tbody:
                for index, row in df.iterrows():
                    with tr(cls="row100 body"):
                        if self.is_index:
                                td(self.index_name[0], cls="cell100 column")

                        for name in self.column_names:
                            td(row[name], cls="cell100 column")

        # Get static requirements
        d_reqts = self.get_table_resources()
        l_js_links = [self.js_static % self.href % r.split('deform:static/')[-1] for r in d_reqts['js']]
        l_css_links = [self.css_static % self.href % r.split('deform:static/')[-1] for r in d_reqts['css']]

        # values passed to template for rendering
        d_web = {
            'table': html,
            'table_css': render_template_string('\n'.join(l_css_links)),
            'table_js': render_template_string('\n'.join(l_js_links)),
        }

        return d_web, d_data


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
