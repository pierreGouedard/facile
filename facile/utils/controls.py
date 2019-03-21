# Global import
from flask import Markup, render_template
from jinja2 import Template

# Local import
from facile.forms.control import ControlForm
from facileapp.models.views.feuille_travaux import FeuilleTravaux
from facileapp.models.devis import Devis
from facileapp.models.facture import Facture
from facileapp.models.user import User
from facile.layout import boostrap
from facile.core.plot_renderer import PlotRerenderer
from facile.tables.html_table import Table


def build_controls(request, session, deform_template_path, script=None, force_get=False):

    if request.args['table'] == 'affaire':
        d_control_data = FeuilleTravaux.control_loading()

    elif request.args['table'] == 'devis':
        d_control_data = Devis.control_loading()

    elif request.args['table'] == 'facture':
        if 'CADMIN' in session['rights'] or 'SADMIN' in session['rights']:
            d_control_data = Facture.control_loading()
        else:
            d_control_data = {
                'restricted':
                    {
                        'rows': [(
                            'title',
                            [{'content': 'title', 'value': "Ce controle est restreint !", 'cls': 'text-center'}])
                        ],
                        'rank': 0
                    }
            }

    elif request.args['table'] == 'users':
        if 'FADMIN' in session['rights'] or 'SADMIN' in session['rights']:
            d_control_data = User.control_loading(session['rights'])
        else:
            d_control_data = {
                'restricted':
                    {
                        'rows': [(
                            'title',
                            [{'content': 'title', 'value': "Ce controle est restreint !", 'cls': 'text-center'}])
                        ],
                        'rank': 0
                    }
            }

    # elif table_key == 'employe':
    #     d_control_data = Employe.control_loading()

    else:
        raise ValueError('key not understood {}'.format(request.args['table_key']))

    l_apps = map(lambda (k, v): k, sorted(d_control_data.items(), key=lambda (k, v): v['rank']))
    template_app_container = Template(
        render_template('control.html', control=Markup(boostrap.get_control_layout(l_apps)))
    )
    html = generic_control_renderer(request, d_control_data, template_app_container, deform_template_path,
                                    script=script, force_get=force_get)

    return html


def generic_control_renderer(request, d_control_data, template_app_container, deform_template_path,
                             script=None,force_get=False):
    d_app_context = {}

    for name, d_data in d_control_data.items():
        template = Template(boostrap.generic_get_layout(d_data['rows'], init='div'))
        d_context, plot_data = {}, None

        for _, row in d_data['rows']:
            for d in row:
                if d['content'] == 'plot':
                    plot_data = d_data['plot']

                elif d['content'] == 'table':
                    d_ = d_data['table']
                    table = Table(d_['df'].columns, 'overview-{}'.format(d_['key']), load_jQuery=True, **d_['kwargs'])
                    d_context['table'] = Markup(table.render_table_from_pandas(d_['df'], d_footer=d_['d_footer']))

                elif d['content'] == 'form':
                    d_context, _ = ControlForm(request, deform_template_path, **d_data['form'])\
                        .process_form(script=script, force_get=force_get)

        if plot_data is not None:
            # Build element of app
            plot_man = PlotRerenderer(plot_data['k'], template, d_context=d_context)

            # Render app element into app template
            d_app_context['app_{}'.format(name)] = Markup(
                plot_man.render_figure(plot_data['d'], **plot_data.get('o', {}))
            )
        else:
            context = {k: Markup(v) for k, v in d_context.items()}
            d_app_context['app_{}'.format(name)] = render_template(template, **context)

    # render app into app container template
    html = render_template(template_app_container, **d_app_context)

    return html


def process_controls(request, session, deform_template_path):
    script = ''

    if request.args['table'] == 'affaire':
        # Load control
        d_control_data = FeuilleTravaux.control_loading()

        # Get form data
        _, form_data = ControlForm(request, deform_template_path, **d_control_data['mergeca']['form']).process_form()

        # Process request and generate qcript response
        script = FeuilleTravaux.control_process(form_data['form_data'])

    elif request.args['table'] == 'users':
        # Load control
        d_control_data = User.control_loading(session['rights'])

        # Get form data
        _, form_data = ControlForm(request, deform_template_path, **d_control_data['setusers']['form']).process_form()

        # Process request and generate qcript response
        script = User.control_process(form_data['form_data'], session)

    return script

