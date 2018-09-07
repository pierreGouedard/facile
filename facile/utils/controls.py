# Global import
from flask import Markup, render_template
from jinja2 import Template

# Local import
from facileapp.models.employe import Employe
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.chantier import Chantier
from facileapp.models.base_prix import Base_prix
from facileapp.models.affaire import Affaire
from facileapp.models.devis import Devis
from facileapp.models.facture import Facture
from facileapp.models.commande import Commande
from facileapp.models.heure import Heure
from facile.layout import boostrap
from facile.core.plot_renderer import PlotRerenderer


def build_controls(table_key):

    if table_key == 'employe':

        d_control_data = Employe.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'fournisseur':
        d_control_data = Fournisseur.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'client':
        d_control_data = Client.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'contact':
        d_control_data = Contact.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'chantier':
        d_control_data = Chantier.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'base_prix':
        d_control_data = Base_prix.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'affaire':
        d_control_data = Affaire.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'devis':
        d_control_data = Devis.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'facture':
        d_control_data = Facture.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'commande':
        d_control_data = Commande.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    elif table_key == 'heure':
        d_control_data = Heure.control_loading()
        template_app_container = Template(
            render_template('control.html', control=Markup(boostrap.get_control_layout(d_control_data.keys())))
        )

    else:
        raise ValueError('key not understood {}'.format(table_key))

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
                    print 'TODO'

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
