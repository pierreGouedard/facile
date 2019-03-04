# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel, engine
from facileapp.models.client import Client
from facileapp.models.contact import Contact


class Chantier(BaseModel):

    name = 'chantier'
    l_index = [StringFields(title='ID', name='chantier_id', widget=HiddenWidget(), table_reduce=True, rank=0,
                            primary_key=True)]
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
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Chantier', name=Chantier.name, dbcols=[f.dbcol() for f in Chantier.l_index + Chantier.l_fields()]
        )

    @staticmethod
    def list(kw):
        if kw == 'client':
            return zip(
                Client.load_db(columns=['designation']).unique(), Client.load_db(columns=['designation']).unique()
            )

        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('chantier', d_index)

        return Chantier(d_index, s.loc[[f.name for f in Chantier.l_fields()]].to_dict())

    @staticmethod
    def from_subindex_(d_subindex):
        d_index = BaseModel.from_subindex('chantier', d_subindex, [f.name for f in Chantier.l_index])
        return Chantier.from_index_(d_index)

    @staticmethod
    def load_db(**kwargs):
        # Get fields
        l_fields = Chantier.l_index + Chantier.l_fields() + Chantier.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='chantier', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_chantier(return_id=False, **kwargs):

        # TODO write the fucking sql request using kwargs mother fucker
        df = pd.read_sql(sql='chantier', con=engine)

        if df.empty:
            return []

        if len(set(kwargs.keys()).intersection(df.columns)) > 0:
            print 'todo'
            # df = df.loc[
            #     df[[c for c in df.columns if c in kwargs.keys()]]
            #     .apply(lambda r: all([str(r[i]) == str(kwargs[i]) for i in r.index]), axis=1)
            # ]

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
        l_chantiers = Chantier.get_chantier(return_id=True)

        # Save current contact id
        chantier_id_ = self.chantier_id

        if self.chantier_id is None or self.chantier_id == '':
            self.chantier_id = 'CH{0:0=4d}'.format(max(l_chantiers, key=lambda t: int(t[0].replace('CH', ''))) + 1)

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