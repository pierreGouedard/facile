from dominate.tags import table, col, thead, tr, th, tbody, td
import jinja2
from flask import render_template_string
import pandas as pd
import settings


class Table(object):

    css_static = '<link rel="stylesheet" type="text/css" href="%s"></link>'
    js_static = '<script type="text/javascript" src="%s"></script>'
    href = "{{url_for('static', filename='table/%s')}}"

    def __init__(self, column_names, is_index=True, index_name=None, fixed_header=True, fixed_index=False,
                 d_sizes=None):

        self.column_names = list(column_names)
        self.is_index = is_index
        self.index_name = []
        if is_index:
            self.index_name = [index_name] if index_name is not None else ['Index']

        self.fixed_header = fixed_header

        if not fixed_header and fixed_index:
            self.fixed_index = True
        else:
            self.fixed_index = False

        if d_sizes is not None:
            self.l_sizes = [(name, d_sizes.get(name, '200px')) for name in self.index_name + self.column_names]
        else:
            self.l_sizes = [(name,  "200px") for name in self.index_name + self.column_names]

    def render_table_from_pandas(self, df):

        # Get static requirements
        d_reqts = self.get_table_resources(self.fixed_index)

        context = {'table_css': render_template_string('\n'.join(d_reqts['css'])),
                   'table_js': render_template_string('\n'.join(d_reqts['js']))}

        # Fixed Head
        if self.fixed_header:
            headtable = self.build_header(self.l_sizes)
            bodytable = self.build_body(df, self.l_sizes, self.is_index, self.column_names)

            # Update context
            context.update({'headtable': headtable, 'bodytable': bodytable})

            # render template
            html = self.render_template('fixedheader.html', context)

        # Fixed columns
        if self.fixed_index:
            indextable = self.build_table(pd.Series(df.index).to_frame(name=self.index_name[0]), self.l_sizes[:1],
                                          self.index_name)
            coretable = self.build_table(df, self.l_sizes[1:], self.column_names)

            # Update context
            context.update({'indextable': indextable, 'coretable': coretable})

            # render template
            html = self.render_template('fixedcolumn.html', context)

        return html

    @staticmethod
    def get_table_resources(is_fixed_index):
        ressources = {'css': [Table.css_static % Table.href % 'css/mainfixedheader.css',
                              Table.css_static % Table.href % 'css/perfect-scrollbar.css'],
                      'js': [Table.js_static % Table.href % 'js/perfect-scrollbar.min.js']
                      }

        if is_fixed_index:
            ressources.update({'css': [Table.css_static % Table.href % 'css/mainfixedcolumn.css',
                                       Table.css_static % Table.href % 'css/perfect-scrollbar.css']
                               })

        return ressources

    @staticmethod
    def render_template(filename, context):
        return jinja2.Environment(loader=jinja2.FileSystemLoader(settings.table_template_path or './'))\
            .get_template(filename)\
            .render(context)

    @staticmethod
    def build_table(df, l_sizes, column_names, is_index=False):
        html_table = table()

        with html_table:
            for _, s in l_sizes:
                col(width=s)
            with thead():
                with tr(cls="row100 head"):
                    for c, _ in l_sizes:
                        th(c, cls="cell100 column")

            with tbody():
                for index, row in df.iterrows():
                    with tr(cls="row100 body"):
                        if is_index:
                            td(index, cls="cell100 column")

                        for name in column_names:
                            td(row[name], cls="cell100 column")

        return html_table

    @staticmethod
    def build_header(l_sizes):
        # Fixed Head !!!!!
        html_head = table()
        with html_head:
            for _, s in l_sizes:
                col(width=s)
            with thead():
                with tr(cls="row100 head"):
                    for c, _ in l_sizes:
                        th(c, cls="cell100 column")

        return html_head

    @staticmethod
    def build_body(df, l_sizes, is_index, column_names):

        html_body = table()
        with html_body:
            for c, s in l_sizes:
                col(width=s)
            with tbody():
                for index, row in df.iterrows():
                    with tr(cls="row100 body"):
                        if is_index:
                            td(index, cls="cell100 column")

                        for name in column_names:
                            td(row[name], cls="cell100 column")

        return html_body
