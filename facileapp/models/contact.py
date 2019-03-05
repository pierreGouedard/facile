# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.client import Client


class Contact(BaseModel):

    table_name = 'contact'
    l_index = [StringFields(title='ID', name='contact_id', widget=HiddenWidget(), missing=-1, table_reduce=True,
                            rank=0, primary_key=True)]
    l_subindex = [1, 2]
    l_actions = map(lambda x: (x.format('un contact'), x.format('un contact')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title='Type de contact', name='type', l_choices=Contact.list('type'), table_reduce=True,
                              rank=1, multiple=True, required=True),
                 StringFields(title='Designation client / fournisseur', name='designation',
                              l_choices=Contact.list('client') + Contact.list('fournisseur'), table_reduce=True, rank=2,
                              required=True),
                 StringFields(title='Designation du contact', name='contact', table_reduce=True, rank=3, required=True),
                 StringFields(title='Description du contact', name='desc', table_reduce=True, rank=4),
                 StringFields(title='Adresse', name='adresse'),
                 StringFields(title='CS/BP', name='cs_bp'),
                 StringFields(title='Ville', name='ville'),
                 StringFields(title='Code postal', name='code_postal'),
                 StringFields(title='tel', name='num_tel'),
                 StringFields(title='E-mail', name='mail')]
        else:
            l_fields = \
                [StringFields(title='Type de contact', name='type', table_reduce=True, rank=1, multiple=True,
                              required=True),
                 StringFields(title='Designation client / fournisseur', name='designation', table_reduce=True, rank=2,
                              required=True),
                 StringFields(title='Designation du contact', name='contact', table_reduce=True, rank=3, required=True),
                 StringFields(title='Description du contact', name='desc', table_reduce=True, rank=4),
                 StringFields(title='Adresse', name='adresse'),
                 StringFields(title='CS/BP', name='cs_bp'),
                 StringFields(title='Ville', name='ville'),
                 StringFields(title='Code postal', name='code_postal'),
                 StringFields(title='tel', name='num_tel'),
                 StringFields(title='E-mail', name='mail')]

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Contact', name=Contact.table_name, dbcols=[f.dbcol() for f in Contact.l_index + Contact.l_fields()]
        )

    @staticmethod
    def list(kw):
        if kw == 'client':
            return zip(Client.load_db()['designation'].unique(), Client.load_db()['designation'].unique())

        elif kw == 'fournisseur':
            return zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs())

        elif kw == 'type':
            return [('client_chantier', 'Contact chantier client'),
                    ('client_administration', 'Contact administratif client'),
                    ('client_commande', 'Contact commande client'),
                    ('fournisseur', 'fournisseur')]

        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('contact', d_index)
        return Contact(d_index, s.loc[[f.name for f in Contact.l_fields()]].to_dict())

    @staticmethod
    def from_subindex_(d_subindex):
        d_index = BaseModel.from_subindex('contact', d_subindex, [f.name for f in Contact.l_index])
        return Contact.from_index_(d_index)

    @staticmethod
    def load_db(**kwargs):

        l_fields = Contact.l_index + Contact.l_fields() + Contact.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='contact', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_contact(type_='all', return_id=False, **kwargs):

        # Get contact of interest
        df = Contact.driver.select(Contact.table_name, **kwargs)

        if df.empty:
            return [('', 'Pas de selection de contact possible')]

        if type_ != 'all':
            df = df.loc[df.type.apply(lambda x: type_ in x)]

        if df.empty:
            return [('', 'Pas de selection de contact possible')]

        d_contacts = df.set_index('contact_id', drop=True)\
            .loc[:, ['designation', 'contact']]\
            .apply(lambda r: '{} / {}'.format(*[r[c] for c in r.index]), axis=1)\
            .to_dict()

        if return_id:
            l_contacts = d_contacts.items()
        else:
            l_contacts = d_contacts.values()

        return l_contacts

    def add(self):
        l_contacts = Contact.get_contact(return_id=True)

        # Save current contact id
        contact_id_ = self.contact_id

        if self.contact_id == '' or self.contact_id is None:
            self.contact_id = 'CT{0:0=4d}'.format(max(map(lambda t: int(t[0].replace('CT', '')), l_contacts)) + 1)

        # Try to add and reset contact id if failed
        try:
            super(Contact, self).add()

        except ValueError, e:
            self.contact_id = contact_id_
            raise ValueError(e.message)

        return self

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            l_subindex = [Contact.l_fields()[i].name for i in Contact.l_subindex]
            d_index = {k: v for k, v in zip(l_subindex, index.split(' / '))}
        else:
            d_index = None

        form_man = FormLoader(Contact.l_index, Contact.l_fields(widget=True), l_subindex=Contact.l_subindex,
                              use_subindex=True)

        if step % Contact.nb_step_form == 0:
            index_node = StringFields(
                title='Nom du contact', name='index', missing=unicode(''),
                l_choices=zip(Contact.get_contact(), Contact.get_contact()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un contact"
            )
            form_man.load_init_form(Contact.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Contact.from_subindex_(d_index).__dict__

            form_man.load(step % Contact.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Contact.load_db()
        table_man = TableLoader(Contact.l_index, Contact.l_fields(), limit=10, type=type)

        if type == 'excel':
            # Get processed table
            df = table_man.load_full_table(df)

            # Save excel file
            writer = pd.ExcelWriter(full_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Feuille1', index=False)
            writer.save()

            return

        if reduced:
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None
        else:
            table_man = TableLoader(Contact.l_index, Contact.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs