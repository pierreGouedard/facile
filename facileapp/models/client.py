# Global imports
import pandas as pd

# Local import
from facile.core.fields import StringFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel


class Client(BaseModel):

    table_name = 'client'
    l_index = [StringFields(title='Designation', name='designation', table_reduce=True, rank=0, primary_key=True)]
    l_actions = map(lambda x: (x.format('un client'), x.format('un client')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        l_fields = \
            [StringFields(title='Raison sociale', name='raison_social', table_reduce=True, rank=1, required=True),
             StringFields(title='Adresse', name='adresse', rank=2, required=True),
             StringFields(title='CS/BP', name='cs_bp'),
             StringFields(title='Ville', name='ville', rank=3, required=True),
             StringFields(title='Code postal', name='code_postal', required=True),
             StringFields(title='tel', name='num_tel', table_reduce=True),
             StringFields(title='E-mail', name='mail', table_reduce=True)]

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Client', name=Client.table_name, dbcols=[f.dbcol() for f in Client.l_index + Client.l_fields()]
        )

    @staticmethod
    def list(kw):
        return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('client', d_index)
        return Client(d_index, s.loc[[f.name for f in Client.l_fields()]].to_dict())

    @staticmethod
    def load_db(**kwargs):
        l_fields = Client.l_index + Client.l_fields() + Client.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='client', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_clients():
        return Client.load_db(columns=['designation'])['designation'].unique()

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Client.l_index[0].name: index}
        else:
            d_index = None

        form_man = FormLoader(Client.l_index, Client.l_fields(widget=True))
        if step % Client.nb_step_form == 0:
            index_node = StringFields(
                title='Designation', name='index', missing='',
                l_choices=zip(Client.get_clients(), Client.get_clients()) + [('new', 'Nouveau')],
                desc="En cas de modification ou supression, choisir la raison sociale du client"
            )
            form_man.load_init_form(Client.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Client.from_index_(d_index).__dict__

            form_man.load(step % Client.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Client.load_db()

        # Instantiate table
        table_man = TableLoader(Client.l_index, Client.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Client.l_index, Client.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs