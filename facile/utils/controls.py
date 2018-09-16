# Global import
from flask import Markup, render_template
from jinja2 import Template

# Local import
from facileapp.models.employe import Employe
from facileapp.models.views.feuille_travaux import FeuilleTravaux
from facileapp.models.base_prix import Base_prix
from facileapp.models.affaire import Affaire
from facileapp.models.devis import Devis
from facileapp.models.facture import Facture
from facileapp.models.commande import Commande
from facileapp.models.heure import Heure
from facile.layout import boostrap
from facile.core.plot_renderer import PlotRerenderer
from facile.tables.html_table import Table


def build_controls(table_key):

    if table_key == 'employe':
        d_control_data = Employe.control_loading()

    elif table_key == 'base_prix':
        d_control_data = Base_prix.control_loading()

    elif table_key == 'affaire':
        d_control_data = FeuilleTravaux.control_loading()

    elif table_key == 'devis':
        d_control_data = Devis.control_loading()

    elif table_key == 'facture':
        d_control_data = Facture.control_loading()

    elif table_key == 'commande':
        d_control_data = Commande.control_loading()

    elif table_key == 'heure':
        d_control_data = Heure.control_loading()

    else:
        raise ValueError('key not understood {}'.format(table_key))

    l_apps = map(lambda (k, v): k, sorted(d_control_data.items(), key=lambda (k, v): v['rank']))
    template_app_container = Template(
        render_template('control.html', control=Markup(boostrap.get_control_layout(l_apps)))
    )
    html = generic_control_renderer(d_control_data, template_app_container)

    return html


def generic_control_renderer(d_control_data, template_app_container):
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
                    print 'TODO'

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
