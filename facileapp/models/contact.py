# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel


class Contact(BaseModel):

    path = os.path.join(settings.facile_project_path, 'contact.csv')

    d_list = {'type': [('client', 'client'),
                       ('fournisseur', 'fournisseur')],

              'client': zip(Client.get_clients(), Client.get_clients()),

              'fournisseur': zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs()),

              'action': [('Ajouter un contact', 'Ajouter un contact'),
                         ('Modifier un contact', 'Modifier un contact'),
                         ('Suprimer un contact', 'Suprimer un contact')]
              }

    l_index = [IntegerFields(title='ID', name='contact_id', widget=HiddenWidget(), missing=-1)]

    l_fields = [StringFields(title='Type de contact', name='type', l_choices=d_list['type']),
                StringFields(title='Raison social du client', name='raison_social',
                             l_choices=d_list['client'] + d_list['fournisseur']),
                StringFields(title='Nom complet du contact', name='contact'),
                StringFields(title='Description du contact', name='desc'),
                StringFields(title='Adresse', name='adresse'),
                StringFields(title='Ville', name='ville'),
                StringFields(title='Code postal', name='code_postal'),
                StringFields(title='tel', name='num_tel'),
                StringFields(title='E-mail', name='mail')]

    l_subindex = [0, 1, 2]

    action_field = StringFields(title='Action', name='action', l_choices=d_list['action'], round=0)
    nb_step_form = 2

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Contact.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Contact(d_index, s.loc[[f.name for f in Contact.l_fields]].to_dict(), path=path)

    @staticmethod
    def from_subindex_(d_subindex, path=None):
        df = Contact.load_db(path)
        d_index = BaseModel.from_subindex(d_subindex, [f.name for f in Contact.l_index], df)
        return Contact.from_index_(d_index, path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Contact.path
        l_fields = Contact.l_index + Contact.l_fields + Contact.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_contact(type_='all', path=None, return_id=False):
        df = Contact.load_db(path)

        if type_ == 'client':
            d_contacts = df.loc[df.type == 'client'].loc[:, ['raison_social', 'contact']]\
                .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1)\
                .to_dict()

        elif type_ == 'fournisseur':
            d_contacts = df.loc[df.type == 'fournisseur'].loc[:, ['raison_social', 'contact']] \
                .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1) \
                .to_dict()

        else:
            d_contacts_f = df.loc[df.type == 'fournisseur'].loc[:, ['raison_social', 'contact']] \
                .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1) \
                .to_dict()

            d_contacts_c = df.loc[df.type == 'client'].loc[:, ['raison_social', 'contact']] \
                .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1)\
                .to_dict()

            d_contacts = {k: 'client - {}'.format(v) for k, v in d_contacts_c.items()}
            d_contacts.update({k: 'fournisseur - {}'.format(v) for k, v in d_contacts_f.items()})

        if return_id:
            l_contacts = d_contacts.items()
        else:
            l_contacts = d_contacts.values()

        return l_contacts

    def add(self):
        df = self.load_db(self.path)
        # Save current contact id
        contact_id_ = self.contact_id

        if self.contact_id == -1 or self.contact_id is None:
            self.contact_id = df.contact_id.apply(lambda x: int(x)).max() + 1

        # Try to add and reset conatct id if failed
        try:
            super(Contact, self).add()
        except ValueError, e:
            self.contact_id = contact_id_
            raise ValueError(e.message)

    @staticmethod
    def form_rendering(step, d_index=None, data=None):

        form_man = FormManager(Contact.l_index, Contact.l_fields, l_subindex=Contact.l_subindex, use_subindex=True)

        if step % Contact.nb_step_form == 0:
            index_node = StringFields(title='Nom complet', name='index', missing=unicode(''),
                                      l_choices=zip(Contact.get_contact(), Contact.get_contact()),
                                      desc="En cas de modification choisir un contact")
            form_man.render_init_form(Contact.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Contact.from_subindex_(d_index).__dict__

            form_man.render(step % Contact.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data
