# Global import
import deform
import colander
from flask import render_template_string


class Form(object):

    appstruct = colander.null
    mapping_name = {'__formid__': None, '_charset_': None}
    css_static = '<link rel="stylesheet" type="text/css" href="%s"></link>'
    js_static = '<script type="text/javascript" src="%s"></script>'
    href = "{{url_for('static', filename='deform/%s')}}"

    def __init__(self, request, search_path, schema):
        self.request = request
        self.search_path = search_path
        self.schema = schema

    def validate_(self, pstruct):
        raise NotImplementedError

    def format_(self, pstruct):
        raise NotImplementedError

    def deffered_missing_(self, pstruct):
        return pstruct

    def process_form(self, **kw):
        success, form_data = False, None

        # Change default renderer path
        deform.form.Form.set_zpt_renderer(self.search_path)

        # Create form
        form = deform.form.Form(self.schema, buttons=('submit',), use_ajax=True)

        # condition of metho
        if self.request.method == 'POST':
            # try to validate the submitted values
            try:

                # parse form
                pstruct = dict([(k, v) for k, v in self.mapping_name.items() + Form.mapping_name.items()])
                pstruct = Form.recursive_parser(pstruct, self.request.form.items(multi=True))

                # Deffered read only input
                self.deffered_missing_(pstruct)

                # Generate succeed form (with values posted)
                captured = form.validate_pstruct(pstruct)

                self.validate_(pstruct)
                html = form.render(captured)

                # Set succes variable and format form data
                success, form_data = True, self.format_(pstruct)

            # the submitted values could not be validated
            except deform.ValidationFailure as e:
                html = e.render()
                success = False

        else:
            # the request requires a simple form rendering
            html = form.render(self.appstruct, **kw)

        # Get static requirements
        d_reqts = form.get_widget_resources()
        l_js_links = [self.js_static % self.href % r.split('deform:static/')[-1] for r in d_reqts['js']]
        l_css_links = [self.css_static % self.href % r.split('deform:static/')[-1] for r in d_reqts['css']]

        # values passed to template for rendering
        d_web = {
            'form': html,
            'form_css': render_template_string('\n'.join(l_css_links)),
            'form_js': render_template_string('\n'.join(l_js_links)),
            }

        # Add form data if Post AND success
        d_data = {'success': success, 'form_data': form_data}

        return d_web, d_data

    @staticmethod
    def recursive_parser(d_out, items):

        # Parse items with d_out
        for k in d_out.keys():
            if isinstance(d_out[k], dict):

                # Get sub list of item for the current key
                items_ = filter(lambda (k_, v_): k in k_, items)
                items_ = map(lambda (k_, v_): (k_.split('{}-'.format(k))[-1], v_), items_)

                # Parse sub element
                d_out[k] = Form.recursive_parser(d_out[k], items_)

            elif isinstance(d_out[k], list):
                items_ = filter(lambda (k_, v_): k in k_, items)
                d_out[k] = [v_ for _, v_ in items_]

            else:
                if k in [k_ for k_, _ in items]:
                    d_out[k] = dict(items)[k]
                else:
                    d_out.pop(k)

        return d_out