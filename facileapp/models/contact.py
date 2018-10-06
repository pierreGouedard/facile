# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.client import Client


class Contact(BaseModel):

    path = os.path.join(settings.facile_project_path, 'contact.csv')
    l_index = [StringFields(title='ID', name='contact_id', widget=HiddenWidget(), missing=-1, table_reduce=True,
                            rank=0)]
    l_subindex = [0, 1, 2]
    l_actions = map(lambda x: (x.format('un contact'), x.format('un contact')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title='Type de contact', name='type', l_choices=Contact.list('type'), table_reduce=True,
                              rank=1),
                 StringFields(title='Raison social du client', name='raison_social',
                              l_choices=Contact.list('client') + Contact.list('fournisseur'), table_reduce=True, rank=2),
                 StringFields(title='Nom complet du contact', name='contact', table_reduce=True, rank=3),
                 StringFields(title='Description du contact', name='desc', table_reduce=True, rank=4),
                 StringFields(title='Adresse', name='adresse'),
                 StringFields(title='Ville', name='ville'),
                 StringFields(title='Code postal', name='code_postal'),
                 StringFields(title='tel', name='num_tel'),
                 StringFields(title='E-mail', name='mail')]
        else:
            l_fields = \
                [StringFields(title='Type de contact', name='type', table_reduce=True, rank=1),
                 StringFields(title='Raison social du client', name='raison_social', table_reduce=True, rank=2),
                 StringFields(title='Nom complet du contact', name='contact', table_reduce=True, rank=3),
                 StringFields(title='Description du contact', name='desc', table_reduce=True, rank=4),
                 StringFields(title='Adresse', name='adresse'),
                 StringFields(title='Ville', name='ville'),
                 StringFields(title='Code postal', name='code_postal'),
                 StringFields(title='tel', name='num_tel'),
                 StringFields(title='E-mail', name='mail')]

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'client':
            return zip(Client.load_db()['raison_social'].unique(), Client.load_db()['raison_social'].unique())

        elif kw == 'fournisseur':
            return zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs())

        elif kw == 'type':
            return [('client', 'client'), ('fournisseur', 'fournisseur')]

        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Contact.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Contact(d_index, s.loc[[f.name for f in Contact.l_fields()]].to_dict(), path=path)

    @staticmethod
    def from_subindex_(d_subindex, path=None):
        df = Contact.load_db(path)
        d_index = BaseModel.from_subindex(d_subindex, [f.name for f in Contact.l_index], df)
        return Contact.from_index_(d_index, path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Contact.path
        l_fields = Contact.l_index + Contact.l_fields() + Contact.l_hfields
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
            self.contact_id = 'CT{0:0=4d}'.format(df.contact_id.apply(lambda x: int(x.replace('CT', ''))).max() + 1)

        # Try to add and reset contact id if failed
        try:
            super(Contact, self).add()

        except ValueError, e:
            self.contact_id = contact_id_
            raise ValueError(e.message)

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            l_subindex = [Contact.l_fields()[i].name for i in Contact.l_subindex]
            d_index = {k: v for k, v in zip(l_subindex, index.split(' - '))}
        else:
            d_index = None

        form_man = FormLoader(Contact.l_index, Contact.l_fields(widget=True), l_subindex=Contact.l_subindex,
                              use_subindex=True)

        if step % Contact.nb_step_form == 0:
            index_node = StringFields(title='Nom du contact', name='index', missing=unicode(''),
                                      l_choices=zip(Contact.get_contact(), Contact.get_contact()),
                                      desc="En cas de modification choisir un contact")
            form_man.load_init_form(Contact.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Contact.from_subindex_(d_index).__dict__

            form_man.load(step % Contact.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True):
        # Load database
        df = Contact.load_db()

        if reduced:
            table_man = TableLoader(Contact.l_index, Contact.l_fields(), limit=10)
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None
        else:
            table_man = TableLoader(Contact.l_index, Contact.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs