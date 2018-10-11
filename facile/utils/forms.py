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
from facile.forms import mutlistep, document


def build_form(table_key, request, deform_template_path, step=0, force_get=True, data=None, validate=True,
               script=None):

    if 'index' in request.form.keys():
        index = request.form['index']
    else:
        index = None

    if table_key == 'employe':
        d_form_data = Employe.form_loading(step, index, data)
        nb_step_form = Employe.nb_step_form

    elif table_key == 'fournisseur':
        d_form_data = Fournisseur.form_loading(step, index, data)
        nb_step_form = Fournisseur.nb_step_form

    elif table_key == 'client':
        d_form_data = Client.form_loading(step, index, data)
        nb_step_form = Fournisseur.nb_step_form

    elif table_key == 'contact':
        d_form_data = Contact.form_loading(step, index, data)
        nb_step_form = Contact.nb_step_form

    elif table_key == 'chantier':
        d_form_data = Chantier.form_loading(step, index, data)
        nb_step_form = Chantier.nb_step_form

    elif table_key == 'base_prix':
        d_form_data = Base_prix.form_loading(step, index, data)
        nb_step_form = Base_prix.nb_step_form

    elif table_key == 'affaire':
        d_form_data = Affaire.form_loading(step, index, data)
        nb_step_form = Affaire.nb_step_form

    elif table_key == 'devis':
        d_form_data = Devis.form_loading(step, index, data)
        nb_step_form = Devis.nb_step_form

    elif table_key == 'facture':
        d_form_data = Facture.form_loading(step, index, data)
        nb_step_form = Facture.nb_step_form

    elif table_key == 'commande':
        d_form_data = Commande.form_loading(step, index, data)
        nb_step_form = Commande.nb_step_form

    elif table_key == 'heure':
        d_form_data = Heure.form_loading(step, index, data)
        nb_step_form = Heure.nb_step_form

    else:
        raise ValueError('key not understood {}'.format(table_key))

    web, data = mutlistep.MultipleStepForm(request, deform_template_path, step, nb_step_form, **d_form_data)\
        .process_form(force_get=force_get, validate=validate, d_format=d_form_data['formatting'], script=script)

    return web, data


def process_form(table_key, d_data, action):

    # Code to download document at the completion of some form (Devis, Affaire, ...)
    data = ('"{}"'.format(table_key), '"{}"'.format(d_data['index']),
            '"{}: {} a bien ete saisie"'.format(table_key, d_data['index']))

    script = '$.ajax({method: "POST", url: "/url_download_form", data: {"table_key": %s, "index": %s}})' \
             '.done(function (response, status, request) { alert(%s);});' % data

    if table_key in ['affaire', 'devis', 'employe']:
        script = '$.ajax({method: "POST", url: "/url_download_form", data: {"table_key": %s, "index": %s}})' \
                 '.done(function (response, status, request) { alert(%s);' \
                 'var url = response["url"].concat(response["data"]);' \
                 'window.location = url;' \
                 '$.ajax({method: "POST", url: "/clean_tmp_dir"});});' % data

    if table_key == 'employe':
        l_index, l_fields = Employe.l_index, Employe.l_fields()
        generic_process_form(l_index, l_fields, Employe, action, d_data=d_data)

    elif table_key == 'fournisseur':
        l_index, l_fields = Fournisseur.l_index, Fournisseur.l_fields()
        generic_process_form(l_index, l_fields, Fournisseur, action, d_data=d_data)

    elif table_key == 'client':
        l_index, l_fields = Client.l_index, Client.l_fields()
        generic_process_form(l_index, l_fields, Client, action, d_data=d_data)

    elif table_key == 'contact':
        l_index, l_fields = Contact.l_index, Contact.l_fields()
        generic_process_form(l_index, l_fields, Contact, action, d_data=d_data)

    elif table_key == 'chantier':
        l_index, l_fields = Chantier.l_index, Chantier.l_fields()
        generic_process_form(l_index, l_fields, Chantier, action, d_data=d_data)

    elif table_key == 'affaire':
        l_index, l_fields = Affaire.l_index, Affaire.l_fields()
        generic_process_form(l_index, l_fields, Affaire, action, d_data=d_data)

    elif table_key == 'base_prix':
        l_index, l_fields = Base_prix.l_index, Base_prix.l_fields()
        generic_process_form(l_index, l_fields, Base_prix, 'Modifier', d_data=d_data)

    elif table_key == 'devis':
        l_index, l_fields = Devis.l_index, [f for f in Devis.l_fields()]
        d_data['price'] = 0
        generic_process_form(l_index, l_fields, Devis, action, d_data)

    elif table_key == 'commande':
        l_index, l_fields = Commande.l_index, [f for f in Commande.l_fields()]
        d_data['montant_ttc'], d_data['montant_tva'] = 0, 0
        generic_process_form(l_index, l_fields, Commande, action, d_data)

    elif table_key == 'facture':
        l_index, l_fields = Facture.l_index, [f for f in Facture.l_fields()]
        d_data['montant_ttc'], d_data['montant_tva'] = 0, 0
        generic_process_form(l_index, l_fields, Facture, action, d_data)

    elif table_key == 'heure':
        l_index, l_fields = Heure.l_index, Heure.l_fields()

        for d_heure in d_data['heure']:
            d_data_ = {k: v for k, v in d_heure.items() + [('semaine', d_data['index'])]}

            if d_heure['heure_id'] == l_index[0].sn.missing:
                generic_process_form(l_index, l_fields, Heure, 'Ajouter', d_data_)
            else:
                generic_process_form(l_index, l_fields, Heure, 'Modifier', d_data_)

    return script


def generic_process_form(l_index, l_fields, model, action, d_data=None):
    if 'Ajouter' in action:
        model({f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_index},
              {f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_fields}) \
            .add()
    elif 'Suprimer' in action:
        model.from_index_({f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_index}).delete()
    else:
        model_ = model.from_index_({f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_index})
        for f in l_fields:
            model_.__setattr__(f.name, f.type(f.processing_db["upload"](d_data[f.name])))
        model_.alter()


def get_args_forms(d_data):

    step = int(d_data['step'])
    if 'Suivant' in d_data.keys():
        step += 1

    elif 'Retour' in d_data.keys():
        step -= 1

    # Get template
    title = get_title_from_step(step, d_data)

    return step, d_data['action'], title


def get_title_from_step(step, data):
    action = data['action']

    if step % int(data['nb_step']) == 0:
        title = 'Choisissez une action'

    else:
        if 'Ajouter' in action:
            title = action

        else:
            title = '{}: {}'.format(action, data.get('index', ''))

    return title


def build_document_form(table_key, request, deform_template_path):

    if table_key == 'employe':
        d_form_data = Employe.form_document_loading()

    elif table_key == 'fournisseur':
        d_form_data = Fournisseur.form_document_loading()

    elif table_key == 'client':
        d_form_data = Client.form_document_loading()

    elif table_key == 'affaire':
        d_form_data = Affaire.form_document_loading()

    elif table_key == 'devis':
        d_form_data = Devis.form_document_loading()

    elif table_key == 'facture':
        d_form_data = Facture.form_document_loading()

    elif table_key == 'commande':
        d_form_data = Commande.form_document_loading()

    else:
        raise ValueError('key not understood {}'.format(table_key))

    web, _ = document.DocumentForm(request, deform_template_path, **d_form_data).process_form()

    return web
