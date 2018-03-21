# Global import
import deform
import colander

class Form(object):

    css_static = '<link rel="stylesheet" type="text/css" href="%s"></link>'
    js_static = '<script type="text/javascript" src="%s"></script>'
    href = "{{url_for('static', filename='deform/%s')}}"

    def __init__(self, request, search_path):
        self.request = request
        self.search_path = search_path

    def render_form(self, form, appstruct=colander.null, **kw):
        success = False

        # condition of metho
        if self.request.method == 'POST':
            # try to validate the submitted values
            try:
                import IPython
                IPython.embed()
                controls = self.order_controls(self.request.form)
                captured = form.validate(controls)
                html = form.render(captured)
                success = True
            # the submitted values could not be validated
            except deform.ValidationFailure as e:
                html = e.render()
                success = False

        else:
            # the request requires a simple form rendering
            html = form.render(appstruct, **kw)

        # Get static requirements
        d_reqts = form.get_widget_resources()
        l_js_links = [self.js_static % self.href % r.split('deform:static/')[-1] for r in d_reqts['js']]
        l_css_links = [self.css_static % self.href % r.split('deform:static/')[-1] for r in d_reqts['css']]

        # values passed to template for rendering
        return {
            'form': html,
            'form_css': '\n'.join(l_css_links),
            'form_js': '\n'.join(l_js_links),
            'success': success
            }

    @staticmethod
    def order_controls(d_controls):
        return d_controls.items()