from dominate.tags import body, div, p, h1
from flask import Markup
import dominate


class BoostrapLayout(object):

    form_template_variable = '{{ form_css }} {{ form_js }} {{ form }}'
    plot_template_variable = '{{ plot_div }} {{ bokeh_js }} {{ bokeh_css }} {{ plot_script }}'
    table_template_variable = '{{ table }}'
    app_template_variable = Markup(u'<div class="jumbotron">{{ app_%s }}</div>')

    def __init__(self, l_rows, init='doc', title='', cls=''):

        self.l_rows = l_rows
        if init == 'doc':
            self.layout = dominate.document(title=title)
        elif init == 'body':
            self.layout = body
        elif init == 'div':
            self.layout = div(id=title, cls=cls)
        else:
            raise ValueError('Init of html document not understood {}'.format(init))

    def build_template(self):
        with self.layout:
            for name, l_cols in self.l_rows:
                with div(cls='row ', id=name):
                    for d_col in l_cols:
                        with div(cls='col-sm-%i {}'.format(d_col.get('cls', '')) % d_col.get('span', 12)):
                            if d_col['content'] == 'app':
                                p(self.app_template_variable % d_col['name'])
                            elif d_col['content'] == 'form':
                                p(self.form_template_variable)
                            elif d_col['content'] == 'plot':
                                p(self.plot_template_variable)
                            elif d_col['content'] == 'table':
                                p(self.table_template_variable)
                            elif d_col['content'] == 'text':
                                p(d_col['value'])
                            elif d_col['content'] == 'title':
                                d_col.get('size', h1)(d_col['value'])


def get_example_layout():
    # Specify rows, columns, there span and content
    l_rows = [('form', [{'span': 12, 'content': 'form'}])]

    # Create layout and build it from l_rows
    layout_example = BoostrapLayout(l_rows, init='div', title='view_example')
    layout_example.build_template()

    return layout_example.layout.render()


def get_form_layout(title):
    # Specify rows, columns, there span and content
    l_rows = [('title', [{'size': h1, 'content': 'title', 'value': title}]),
              ('form', [{'span': 12, 'content': 'form'}]),
              ('table', [{'span': 12, 'content': 'table'}])]

    # Create layout and build it from l_rows
    layout_form = BoostrapLayout(l_rows, init='div', title='view_form')
    layout_form.build_template()

    return layout_form.layout.render()


def get_export_layout(title):
    # Specify rows, columns, there span and content
    l_rows = [('title', [{'size': h1, 'content': 'title', 'value': title}]),
              ('table', [{'span': 12, 'content': 'table'}]),
              ('form', [{'span': 12, 'content': 'form'}])]

    # Create layout and build it from l_rows
    layout_export = BoostrapLayout(l_rows, init='div', title='view_export')
    layout_export.build_template()

    return layout_export.layout.render()


def get_document_layout(title):
    # Specify rows, columns, there span and content
    l_rows = [('title', [{'size': h1, 'content': 'title', 'value': title}]),
              ('form', [{'span': 12, 'content': 'form'}])]

    # Create layout and build it from l_rows
    layout_document = BoostrapLayout(l_rows, init='div', title='view_document')
    layout_document.build_template()

    return layout_document.layout.render()


def get_control_layout(l_app):
    # Specify rows, columns, there span and content
    l_rows = [('app_{}'.format(i), [{'span': 12, 'content': 'app', 'name': name}]) for i, name in enumerate(l_app)]

    # Create layout and build it from l_rows
    layout_control = BoostrapLayout(l_rows, init='div', title='view_control')
    layout_control.build_template()

    return layout_control.layout.render()


def get_login_layout():

    l_rows = [('login', [{'span': 12, 'content': 'form'}])]

    # Create layout and build it from l_rows
    layout_login = BoostrapLayout(l_rows, init='div', title='view_series')
    layout_login.build_template()

    return layout_login.layout.render()


def get_other_layout():

    l_rows = [('Other', [{'span': 12, 'content': 'form'}])]

    # Create layout and build it from l_rows
    layout_other = BoostrapLayout(l_rows, init='div', title='view_other')
    layout_other.build_template()

    return layout_other.layout.render()


def generic_get_layout(l_rows, init='div', title='', cls=''):

    # Create layout and build it from l_rows
    layout = BoostrapLayout(l_rows, init=init, title=title, cls=cls)
    layout.build_template()

    return layout.layout.render()
