from facileapp.models import Employe, Fournisseur, Client, Contact, Chantier, Base_prix, Affaire, Devis
from facile.forms import mutliform


def build_form(table_key, request, deform_template_path, step=0, force_get=True, data={}, validate=True):

    if table_key == 'employe':
        if step % Employe.nb_step_form == 0:
            d_index = None
        else:
            action = request.form['action']

            if 'Modifier' in action or 'Suprimer' in action:
                l_index = [sch.name for sch in Employe.l_index]
                d_index = {k: v for k, v in zip(l_index, request.form['index'].split('-'))}
            else:
                d_index = None

        d_form_data = Employe.form_rendering(step, d_index, data)
        nb_step_form = Employe.nb_step_form

    elif table_key == 'fournisseur':
        if step % Fournisseur.nb_step_form == 0:
            d_index = None
        else:
            action = request.form['action']

            if 'Modifier' in action or 'Suprimer' in action:
                index = Fournisseur.l_index[0].name
                d_index = {index: request.form['index']}
            else:
                d_index = None

        d_form_data = Fournisseur.form_rendering(step, d_index, data)
        nb_step_form = Fournisseur.nb_step_form

    elif table_key == 'client':
        if step % Client.nb_step_form == 0:
            d_index = None
        else:
            action = request.form['action']

            if 'Modifier' in action or 'Suprimer' in action:
                index = Client.l_index[0].name
                d_index = {index: request.form['index']}
            else:
                d_index = None

        d_form_data = Client.form_rendering(step, d_index, data)
        nb_step_form = Fournisseur.nb_step_form

    elif table_key == 'contact':
        if step % Contact.nb_step_form == 0:
            d_index = None
        else:
            action = request.form['action']

            if 'Modifier' in action or 'Suprimer' in action:
                l_subindex = [Contact.l_fields[i].name for i in Contact.l_subindex]
                d_index = {k: v for k, v in zip(l_subindex, request.form['index'].split(' - '))}
            else:
                d_index = None

        d_form_data = Contact.form_rendering(step, d_index, data)
        nb_step_form = Contact.nb_step_form

    elif table_key == 'chantier':
        if step % Chantier.nb_step_form == 0:
            d_index = None
        else:
            action = request.form['action']

            if 'Modifier' in action or 'Suprimer' in action:
                l_subindex = [Chantier.l_fields[i].name for i in Chantier.l_subindex]
                d_index = {k: v for k, v in zip(l_subindex, request.form['index'].split(' - '))}
            else:
                d_index = None

        d_form_data = Chantier.form_rendering(step, d_index, data)
        nb_step_form = Chantier.nb_step_form

    elif table_key == 'base_prix':
        if step % Base_prix.nb_step_form == 0:
            d_index = None

        else:
            index = Base_prix.l_index[0].name
            d_index = {index: request.form['index']}

        d_form_data = Base_prix.form_rendering(step, d_index, data)
        nb_step_form = Base_prix.nb_step_form

    elif table_key == 'affaire':
        if step % Affaire.nb_step_form == 0:
            d_index = None

        else:
            if 'Modifier' in request.form['action'] or 'Suprimer' in request.form['action']:
                index = Affaire.l_index[0].name
                d_index = {index: request.form['index']}
            else:
                d_index = None

        d_form_data = Affaire.form_rendering(step, d_index, data)
        nb_step_form = Affaire.nb_step_form

    elif table_key == 'devis':
        if step % Devis.nb_step_form == 0:
            d_index = None
        else:
            if 'Modifier' in request.form['action'] or 'Suprimer' in request.form['action']:
                f_index = Devis.l_index[0]
                d_index = {f_index.name: f_index.type(request.form['index'])}
            else:
                d_index = None

        d_form_data = Devis.form_rendering(step, d_index, data)
        nb_step_form = Devis.nb_step_form

    elif table_key == 'heure':

        import colander
        import deform

        class ArticleMapping(colander.Schema):
            name = 'article'

        article = ArticleMapping()
        article.add(colander.SchemaNode(colander.Integer(), name='article-quantite'))
        article.add(colander.SchemaNode(colander.Integer(), name='article-prix_unit'))
        article.add(colander.SchemaNode(colander.Integer(), name='article-description'))

        sequence = colander.SchemaNode(
                colander.Sequence(),
                article
            )

        d_form_data = {'nodes': [sequence], 'buttons': ('submit',),
                       'mapping': {'article': [{'quantite': None, 'description': None, 'prix_unit': None}]}
                       }
        step, action, nb_step_form = 0, None, 1

    else:
        raise ValueError('key not understood {}'.format(table_key))

    web, data = mutliform.MultipleStepForm(request, deform_template_path, step, nb_step_form, **d_form_data)\
        .process_form(force_get=force_get, validate=validate, d_format=d_form_data['formatting'])

    return web, data


def process_form(table_key, d_data, action):

    if table_key == 'employe':
        d_data['date_start'] = d_data['date_start']['date']
        d_data['date_end'] = d_data['date_end']['date']

        if 'Modifier' in action or 'Suprimer' in action:
            employe = Employe.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Employe.l_index})

            for sch in Employe.l_fields:
                employe.__setattr__(sch.name, sch.type(d_data[sch.name]))
            if 'Modifier' in action:
                employe.alter()
            else:
                employe.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Employe.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Employe.l_fields}

            employe = Employe(d_index, d_fields)
            employe.add()

    elif table_key == 'fournisseur':

        if 'Modifier' in action or 'Suprimer' in action:
            fournisseur = Fournisseur.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Fournisseur.l_index})

            for sch in Fournisseur.l_fields:
                fournisseur.__setattr__(sch.name, sch.type(d_data[sch.name]))
            if 'Modifier' in action:
                fournisseur.alter()
            else:
                fournisseur.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Fournisseur.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Fournisseur.l_fields}

            fournisseur = Fournisseur(d_index, d_fields)
            fournisseur.add()

    elif table_key == 'client':

        if 'Modifier' in action or 'Suprimer' in action:
            client = Client.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Client.l_index})

            for sch in Client.l_fields:
                client.__setattr__(sch.name, sch.type(d_data[sch.name]))
            if 'Modifier' in action:
                client.alter()
            else:
                client.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Client.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Client.l_fields}

            client = Client(d_index, d_fields)
            client.add()

    elif table_key == 'contact':

        if 'Modifier' in action or 'Suprimer' in action:
            contact = Contact.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Contact.l_index})

            for sch in Contact.l_fields:
                contact.__setattr__(sch.name, sch.type(d_data[sch.name]))
            if 'Modifier' in action:
                contact.alter()
            else:
                contact.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Contact.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Contact.l_fields}

            contact = Contact(d_index, d_fields)
            contact.add()

    elif table_key == 'chantier':

        if 'Modifier' in action or 'Suprimer' in action:
            chantier = Chantier.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Chantier.l_index})

            for sch in Chantier.l_fields:
                chantier.__setattr__(sch.name, sch.type(d_data[sch.name]))
            if 'Modifier' in action:
                chantier.alter()
            else:
                chantier.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Chantier.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Chantier.l_fields}

            chantier = Chantier(d_index, d_fields)
            chantier.add()

    elif table_key == 'affaire':

        if 'Modifier' in action or 'Suprimer' in action:
            affaire = Affaire.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Affaire.l_index})

            for sch in Affaire.l_fields:
                affaire.__setattr__(sch.name, d_data[sch.name])
            if 'Modifier' in action:
                affaire.alter()
            else:
                affaire.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Affaire.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Affaire.l_fields}

            chantier = Affaire(d_index, d_fields)
            chantier.add()

    elif table_key == 'base_prix':

        base_prix = Base_prix.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Base_prix.l_index})

        for sch in Base_prix.l_fields:
            base_prix.__setattr__(sch.name, sch.type(d_data[sch.name]))

        base_prix.alter()

    elif table_key == 'devis':

        if 'Modifier' in action or 'Suprimer' in action:
            devis = Chantier.from_index_({sch.name: sch.type(d_data[sch.name]) for sch in Devis.l_index})

            for sch in Chantier.l_fields:
                devis.__setattr__(sch.name, sch.type(d_data[sch.name]))
            if 'Modifier' in action:
                devis.alter()
            else:
                devis.delete()

        elif 'Ajouter' in action:
            d_index = {sch.name: sch.type(d_data[sch.name]) for sch in Devis.l_index}
            d_fields = {sch.name: sch.type(d_data[sch.name]) for sch in Deviss.l_fields}

            devis = Devis(d_index, d_fields)
            devis.add()


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
    if 'Ajouter' in data['action']:
        title = action if step % int(data['nb_step']) > 0 else 'Choisissez une action'
    else:
        title = '{}: {}'.format(action, data.get('index', '')) if step % int(data['nb_step']) > 0 \
            else 'Choisissez une action'

    return title