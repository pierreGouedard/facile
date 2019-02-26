# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.client import Client
from facileapp.models.contact import Contact


class Chantier(BaseModel):

    path = os.path.join(settings.facile_db_path, 'chantier.csv')
    l_index = [StringFields(title='ID', name='chantier_id', widget=HiddenWidget(), table_reduce=True, rank=0)]
    l_subindex = [0, 1]
    l_actions = map(lambda x: (x.format('un chantier'), x.format('un chantier')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title='Designation du client', name='designation_client', l_choices=Chantier.list('client'),
                              table_reduce=True, rank=1, required=True),
                 StringFields(title='Designation du chantier', name='nom', table_reduce=True, rank=2, required=True),
                 StringFields(title='Adresse', name='adresse', required=True),
                 StringFields(title='Ville', name='ville', required=True),
                 StringFields(title='Code postal', name='code_postal', required=True),
                 ]
        else:
            l_fields = \
                [StringFields(title='Designation du client', name='designation_client', table_reduce=True, rank=1,
                              required=True),
                 StringFields(title='Designation du chantier', name='nom', table_reduce=True, rank=2, required=True),
                 StringFields(title='Adresse', name='adresse', required=True),
                 StringFields(title='Ville', name='ville', required=True),
                 StringFields(title='Code postal', name='code_postal', required=True),
                 ]

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'client':
            return zip(Client.load_db()['designation'].unique(), Client.load_db()['designation'].unique())

        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Chantier.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Chantier(d_index, s.loc[[f.name for f in Chantier.l_fields()]].to_dict(), path=path)

    @staticmethod
    def from_subindex_(d_subindex, path=None):
        df = Chantier.load_db(path)
        d_index = BaseModel.from_subindex(d_subindex, [f.name for f in Chantier.l_index], df)
        return Chantier.from_index_(d_index, path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Chantier.path
        l_fields = Chantier.l_index + Chantier.l_fields() + Chantier.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_chantier(path=None, return_id=False, **kwargs):

        # Load chantier database and apply filter if any in kwargs
        df = Chantier.load_db(path)

        if df.empty:
            return []

        if len(set(kwargs.keys()).intersection(df.columns)) > 0:
            df = df.loc[
                df[[c for c in df.columns if c in kwargs.keys()]]
                .apply(lambda r: all([str(r[i]) == str(kwargs[i]) for i in r.index]), axis=1)
            ]

        df = df.set_index('chantier_id', drop=True)\
            .loc[:, ['designation_client', 'nom']] \
            .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1) \
            .to_dict()

        if return_id:
            l_chantier = df.items()

        else:
            l_chantier = df.values()

        return l_chantier

    def add(self):

        df = self.load_db(self.path)

        # Save current contact id
        chantier_id_ = self.chantier_id

        if self.chantier_id is None or self.chantier_id == '':
            self.chantier_id = 'CH{0:0=4d}'.format(df.chantier_id.apply(lambda x: int(x.replace('CH', ''))).max() + 1)

        # Try to add and reset conatct id if failed
        try:
            super(Chantier, self).add()
        except ValueError, e:
            self.chantier_id = chantier_id_
            raise ValueError(e.message)

        return self

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            l_subindex = [Chantier.l_fields()[i].name for i in Contact.l_subindex]
            d_index = {k: v for k, v in zip(l_subindex, index.split(' - '))}
        else:
            d_index = None

        form_man = FormLoader(Chantier.l_index, Chantier.l_fields(widget=True), l_subindex=Chantier.l_subindex,
                              use_subindex=True)

        if step % Chantier.nb_step_form == 0:
            index_node = StringFields(
                title='Nom du chantier', name='index', missing=unicode(''),
                l_choices=zip(Chantier.get_chantier(), Chantier.get_chantier()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un chantier"
            )
            form_man.load_init_form(Chantier.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Chantier.from_subindex_(d_index).__dict__

            form_man.load(step % Chantier.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Chantier.load_db()
        table_man = TableLoader(Chantier.l_index, Chantier.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Chantier.l_index, Chantier.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs