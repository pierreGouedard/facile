# Global import
import mimetypes

# Local import
from facileapp.models.employe import Employe
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.chantier import Chantier
from facileapp.models.affaire import Affaire
from facileapp.models.devis import Devis
from facileapp.models.facture import Facture
from facileapp.models.commande import Commande
from facileapp.models.heure import Heure
from facileapp.models.views.feuille_travaux import FeuilleTravaux
from facileapp.models.views.facturation import Facturation
from facileapp.models.views.achat import Achat
from facile.utils.drivers.files import FileDriver
from facile.forms import mutlistep, document
from settings import facile_driver_tmpdir, facile_commande_path


def build_form(table_key, request, deform_template_path, step=0, force_get=True, data={}, validate=True,
               script=None):

    if 'index' in request.form.keys() and 'Ajouter' not in data.get('action', ''):
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
        nb_step_form = Client.nb_step_form

    elif table_key == 'contact':
        d_form_data = Contact.form_loading(step, index, data)
        nb_step_form = Contact.nb_step_form

    elif table_key == 'chantier':
        d_form_data = Chantier.form_loading(step, index, data)
        nb_step_form = Chantier.nb_step_form

    elif table_key == 'affaire':
        if index is None and 'secondaire' in data.get('action', ''):
            index = request.form['index']

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
    script = '$.ajax({method: "POST", url: "/url_download_form", data: {"table_key": %s, "index": %s}})' \
             '.done(function (response, status, request) {alert(%s %s);});'

    if table_key in ['affaire', 'devis', 'facture', 'commande'] and 'Suprimer' not in action:
        script = '$.ajax({method: "POST", url: "/url_download_form", data: {"table_key": %s, "index": %s}})' \
                 '.done(function (response, status, request) { alert(%s %s);' \
                 'var url = response["url"].concat(response["data"]);' \
                 'window.location = url});'

    if table_key == 'employe':
        l_index, l_fields = Employe.l_index, Employe.l_fields()
        statue = generic_process_form(l_index, l_fields, Employe, action, d_data=d_data, table_key=table_key)

    elif table_key == 'fournisseur':
        l_index, l_fields = Fournisseur.l_index, Fournisseur.l_fields()
        statue = generic_process_form(l_index, l_fields, Fournisseur, action, d_data=d_data, table_key=table_key)

    elif table_key == 'client':
        l_index, l_fields = Client.l_index, Client.l_fields()
        statue = generic_process_form(l_index, l_fields, Client, action, d_data=d_data, table_key=table_key)

    elif table_key == 'contact':
        l_index, l_fields = Contact.l_index, Contact.l_fields()
        statue = generic_process_form(l_index, l_fields, Contact, action, d_data=d_data, table_key=table_key)

    elif table_key == 'chantier':
        l_index, l_fields = Chantier.l_index, Chantier.l_fields()
        statue = generic_process_form(l_index, l_fields, Chantier, action, d_data=d_data, table_key=table_key)

    elif table_key == 'affaire':
        l_index, l_fields = Affaire.l_index, Affaire.l_fields()
        statue = generic_process_form(l_index, l_fields, Affaire, action, d_data=d_data, table_key=table_key)

    elif table_key == 'devis':
        l_index, l_fields = Devis.l_index, [f for f in Devis.l_fields()]
        d_data['price'] = 0
        statue = generic_process_form(l_index, l_fields, Devis, action, d_data, table_key=table_key)

    elif table_key == 'commande':
        filename = ''.join(['{}', mimetypes.guess_extension(d_data['details']['mimetype'])])
        d_files = {FileDriver('', '').join(facile_commande_path, filename): d_data['details']['fp']}

        l_index, l_fields = Commande.l_index, [f for f in Commande.l_fields()]
        d_data['montant_ttc'], d_data['montant_tva'] = 0, 0
        statue = generic_process_form(l_index, l_fields, Commande, action, d_data, table_key=table_key, d_files=d_files)

    elif table_key == 'facture':
        l_index, l_fields = Facture.l_index, [f for f in Facture.l_fields()]
        d_data['montant_ttc'], d_data['montant_tva'] = 0, 0
        statue = generic_process_form(l_index, l_fields, Facture, action, d_data, table_key=table_key)

    elif table_key == 'heure':
        l_index, l_fields, statue = Heure.l_index, Heure.l_fields(), {'success': True}

        # Load current database of hours
        df, l_hid = Heure.load_db(), []
        df = df.loc[df['semaine'] == d_data['index']]

        # Alter or add hours that have been sent
        for d_heure in d_data['heure']:
            d_data_ = {k: v for k, v in d_heure.items() + [('semaine', d_data['index']), ('index', d_data['index'])]}

            if d_heure['heure_id'] == l_index[0].sn.missing:
                statue = generic_process_form(l_index, l_fields, Heure, 'Ajouter', d_data_, table_key=table_key)
            else:
                l_hid += [d_data_[l_index[0].name]]
                statue = generic_process_form(l_index, l_fields, Heure, 'Modifier', d_data_, table_key=table_key)

        # Remove hours that have been deleted if any
        for hid in set(df.heure_id.values).difference(l_hid):
            d_data_ = {'index': d_data['index'], l_index[0].name: hid}
            statue = generic_process_form(l_index, l_fields, Heure, 'Suprimer', d_data_, table_key=table_key)

        if 'success' in statue:
            statue.update(
                {'data': ('"{}"'.format(table_key), '"{}"'.format(d_data['index']),
                          '"{}: {}'.format(table_key, d_data['index']),
                          ' {} avec succes"'.format("edite"))}
            )
    else:
        statue = {'error': 'Unknown table'}

    if 'success' not in statue:
        if statue['error'] == 'index':
            script = \
                'alert("Erreur: l\'element {} existe dans la base. Modifier l\'element existant ou changer la valeur' \
                ' du champ {}");'.format(statue['index'], statue['index_name'])

        else:
            raise ValueError('{}'.format(statue))

    else:
        script = script % statue['data']
    return script


def generic_process_form(l_index, l_fields, model, action, d_data=None, table_key=None, d_files=None):

    # Get data to alert successful
    data = ('"{}"'.format(table_key), '"{}"'.format(d_data['index']),
            '"{}: {}'.format(table_key, d_data['index']),
            '{} avec succes"'.format(action))

    if 'Ajouter' in action:
        try:
            m = model({f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_index},
                      {f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_fields}) \
                .add()

            index = '/'.join(map(str, [m.__getattribute__(f.name) for f in l_index]))
            data = ('"{}"'.format(table_key), '"{}"'.format(index),
                    '"{}: {}'.format(table_key, index.replace('/', ' ')),
                    '{} avec succes"'.format(action))

            if d_files is not None:
                import IPython
                IPython.embed()
                # TODO: save in tmpdir and upload to s3
                for k, v in d_files.items():
                    v.save(k.format(index.replace('/', '_')))

        except IndexError:
            error = {'error': 'index',
                     'index': [d_data.get(f.name, f.sn.missing) for f in l_index],
                     'index_name': [f.name for f in l_index]}
            return error

    elif 'Suprimer' in action:
        model.from_index_({f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_index}).delete()

    else:
        model_ = model.from_index_({f.name: f.type(f.processing_db["upload"](d_data[f.name])) for f in l_index})
        for f in l_fields:
            model_.__setattr__(f.name, f.type(f.processing_db["upload"](d_data[f.name])))
        model_.alter()

    return {'success': True, 'data': data}


def get_args_forms(d_data):

    step = int(d_data['step'])
    if 'Suivant' in d_data.keys():
        step += 1

    elif 'Retour' in d_data.keys():
        step -= 1

    # Get template
    title = get_title_from_step(step, d_data)

    # get action
    if 'Ajouter' in d_data['action']:
        action = 'Ajouter'
    elif 'Modifier' in d_data['action']:
        action = 'Modifier'
    elif 'Suprimer' in d_data['action']:
        action = 'Suprimer'
    else:
        action = d_data['action']

    return step, action, title


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

    if table_key == 'affaire':
        d_form_data = FeuilleTravaux.form_document_loading()

    elif table_key == 'devis':
        d_form_data = Devis.form_document_loading()

    elif table_key == 'facture':
        d_form_data = Facturation.form_document_loading()

    elif table_key == 'commande':
        d_form_data = Achat.form_document_loading()
    else:
        raise ValueError('key not understood {}'.format(table_key))

    web, _ = document.DocumentForm(request, deform_template_path, **d_form_data).process_form()

    return web


def process_document_form(table_key, d_request):

    # Clean facile doc tmpdir
    clean_tmp_dir()

    # Create tmp dir
    driver = FileDriver('tmp_doc', '')
    tmpdir = driver.TempDir(create=True, prefix='tmp_doc_')

    if table_key == 'affaire':
        d_index = {f.name: c for f, c in zip(Affaire.l_index, d_request['index'].split('/'))}
        FeuilleTravaux.document_(d_index, tmpdir.path, driver, name='doc_fdt.docx')
        full_path = driver.join(tmpdir.path, 'doc_fdt.docx')

    elif table_key == 'devis':
        d_index = {Devis.l_index[0].name: d_request['index']}
        Devis.document_(d_index, tmpdir.path, driver, name='doc_devis.docx')
        full_path = driver.join(tmpdir.path, 'doc_devis.docx')

    elif table_key == 'facture':
        d_index = {Facture.l_index[0].name: d_request['index']}
        Facturation.document_(d_index, tmpdir.path, driver, name='doc_facture.docx')
        full_path = driver.join(tmpdir.path, 'doc_facture.docx')

    elif table_key == 'commande':
        d_index = {Commande.l_index[0].name: d_request['index']}
        Achat.document_(d_index, tmpdir.path, driver, name='doc_achat.docx')
        full_path = driver.join(tmpdir.path, 'doc_achat.docx')

    else:
        raise ValueError('key not understood {}'.format(table_key))

    return full_path, tmpdir


def clean_tmp_dir():
    driver = FileDriver('tmp_doc', '')
    for f in driver.listdir(facile_driver_tmpdir):
        if 'tmp_doc_' in f:
            try:
                driver.remove(driver.join(facile_driver_tmpdir, f), recursive=True)
            except OSError:
                continue
