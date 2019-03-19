from dominate.tags import table, col, thead, tr, th, tbody, td, tfoot
import jinja2
from flask import render_template_string, Markup
from config import TABLE_TEMPLATE_PATH


class Table(object):
    """
    Load jquery enable te sort, search , ... functionality yet the jquery version conflicts with the form jquery
    dependance, it may be solved more properly but have no time (i.e if need a very simple table along with form, don't
    load the jquery, for exploration work without form, use jquery and  all nice options)
    """
    css_static = '<link rel="stylesheet" type="text/css" href="%s"></link>'
    js_static = '<script type="text/javascript" src="%s"></script>'
    jquery = "<script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.0.0-beta1/jquery.js'></script>"
    href = "{{url_for('static', filename='table/%s')}}"

    def __init__(self, column_names, id_table, head_class='table-active', style='underscore', load_jQuery=False,
                 **kwargs):

        self.column_names = list(column_names)
        self.id_table = id_table
        self.has_footer = kwargs.get('has_footer', False)
        self.foot_class = kwargs.get('foot_class', 'table-active')
        self.responsive = kwargs.get('responsive', False)

        # Get params
        features = "paginate: {}, sort: {}, pushState: true, search: {}, recordCount: {}, perPageSelect: {}"
        features = features.format(*[kwargs.get('paginate', 'false'), kwargs.get('sort', 'false'),
                                     kwargs.get('search', 'false'), kwargs.get('record_cnt', 'false'),
                                     kwargs.get('per_page', 'false')])
        features = 'features: {}'.format('{' + features + '}')

        table = "defaultColumnIdStyle: '{}', headRowClass: '{}'".format(style, head_class)
        table = 'table: {}'.format('{' + table + '}')
        self.params = "{}, {}".format('{' + features, table + '}')

        self.load_jQuery = load_jQuery

    def render_table_from_pandas(self, df, d_footer=None):

        # Get static requirements
        context = {'ressource': self.get_table_resources(self.load_jQuery)}

        # Fixed Head
        headtable = self.build_header(self.column_names)
        bodytable = self.build_body(df, self.column_names)

        if self.has_footer and d_footer is not None:
            foottable = self.build_footer(d_footer, self.column_names, self.foot_class)
        else:
            foottable = ''

        if self.responsive:
            resp = 'table-responsive'
        else:
            resp = ''

        # Update context
        context.update(
            {'id_table': self.id_table, 'responsive': resp, 'headtable': headtable, 'bodytable': bodytable,
             'foottable': foottable, 'table_js': Markup("<script>$('#{}').dynatable({})</script>"
                                                        .format(self.id_table, self.params))}
        )

        # render template
        html = self.render_template('table.html', context)

        return html

    @staticmethod
    def get_table_resources(load_jQuery):
        if load_jQuery:
            l_ressources = [Table.jquery]
        else:
            l_ressources = []

        l_ressources += [render_template_string(Table.css_static % Table.href % 'css/jquery.dynatable.css'),
                         render_template_string(Table.js_static % Table.href % 'js/jquery.dynatable.js')]

        ressources = "\n".join(l_ressources)

        return ressources

    @staticmethod
    def render_template(filename, context):
        return jinja2.Environment(loader=jinja2.FileSystemLoader(TABLE_TEMPLATE_PATH or './'))\
            .get_template(filename)\
            .render(context)

    @staticmethod
    def build_header(l_cols):
        html_head = thead()
        with html_head:
            with tr():
                for c in l_cols:
                    th(c.decode('latin1'))

        return html_head

    @staticmethod
    def build_body(df, l_cols):

        html_body = tbody()
        with html_body:
            for index, row in df.iterrows():
                with tr():
                    for name in l_cols:
                        td(str(row[name]).decode('latin1'), cls="table-primary")

        return html_body

    @staticmethod
    def build_footer(row, l_cols, cls):

        html_foot = tfoot(cls=cls)
        with html_foot:
            with tr():
                for name in l_cols:
                    td(row[name], cls="table-primary")

        return html_foot
