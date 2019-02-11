# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, MoneyFields, DateFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire


class Facture(BaseModel):

    path = os.path.join(settings.facile_project_path, 'facture.csv')
    l_index = [StringFields(title='Numero de Facture', name='facture_id', widget=HiddenWidget(), table_reduce=True,
                            rank=0)]
    l_actions = map(lambda x: (x.format('une facture'), x.format('une facture')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title="Numero d'affaire", name='affaire_id', l_choices=Facture.list('affaire'),
                              table_reduce=True, rank=1),
                 StringFields(title='Type', name='type', l_choices=Facture.list('type'), table_reduce=True),
                 StringFields(title='Objet', name='objet'),
                 MoneyFields(title='Montant facture HT', name='montant_ht'),
                 IntegerFields(title='Numero de situation', name='situation', l_choices=Facture.list('situation')),
                 DateFields(title='Visa', name='date_visa'),
                 DateFields(title='Encaissement', name='date_payed')
                 ]
        else:
            l_fields = \
                [StringFields(title="Numero d'affaire", name='affaire_id', table_reduce=True, rank=1),
                 StringFields(title='Type', name='type', table_reduce=True),
                 StringFields(title='Objet', name='objet'),
                 MoneyFields(title='Montant facture HT', name='montant_ht'),
                 IntegerFields(title='Numero de situation', name='situation'),
                 DateFields(title='Visa', name='date_visa'),
                 DateFields(title='Encaissement', name='date_payed')]

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'affaire':
            return zip(Affaire.get_affaire(sep='-'), map(str, Affaire.get_affaire(sep=' - ')))
        elif kw == 'situation':
            return [(i, 'Situation numero {}'.format(i)) for i in range(1, 13)]
        elif kw == 'type':
            return [('facture', 'Facture'), ('avoir', 'Avoir')]
        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Facture.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Facture(d_index, s.loc[[f.name for f in Facture.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Facture.path

        return pd.read_csv(path, dtype={f.name: f.type for f in Facture.l_index + Facture.l_fields() + Facture.l_hfields}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in Facture.l_index + Facture.l_fields() + Facture.l_hfields})

    @staticmethod
    def get_facture(path=None):
        return Facture.load_db(path)['facture_id'].unique()

    def add(self):
        df = self.load_db(self.path)

        # Save current facture id
        facture_id_ = self.facture_id

        if self.facture_id == '' or self.facture_id is None:
            df = df.loc[df.type == self.type]

            if self.type == 'facture':
                self.facture_id = 'FC{0:0=4d}'.format(df.facture_id.apply(lambda x: int(x.replace('FC', ''))).max() + 1)

            else:
                self.facture_id = 'AV{0:0=4d}'.format(df.facture_id.apply(lambda x: int(x.replace('AV', ''))).max() + 1)
                if self.montant_ht > 0:
                    self.montant_ht *= -1

        # Try to add and reset conatct id if failed
        try:
            super(Facture, self).add()

        except ValueError, e:
            self.facture_id = facture_id_
            raise ValueError(e.message)

        return self

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Facture.l_index[0].name: Facture.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormLoader(Facture.l_index, Facture.l_fields(widget=True))

        if step % Facture.nb_step_form == 0:
            index_node = StringFields(
                title='Numero de facture', name='index', missing=-1,
                l_choices=zip(Facture.get_facture(), Facture.get_facture()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un numero de facture"
            )
            form_man.load_init_form(Facture.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Facture.from_index_(d_index).__dict__

            form_man.load(step % Facture.nb_step_form, data_db=data_db, data_form=data)

        print form_man.d_form_data
        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True):
        # Load database
        df = Facture.load_db()

        if reduced:
            table_man = TableLoader(Facture.l_index, Facture.l_fields(), limit=10)
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None
        else:
            table_man = TableLoader(Facture.l_index, Facture.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Facture.load_db()

        # App 1 repartition bill waiting for visa, waiting for payment, payed for current business year
        df_statue = df[['is_visa', 'is_payed', 'montant_ht']].groupby(['is_visa', 'is_payed'])\
            .sum()\
            .reset_index()
        df_statue['name'] = df_statue[['is_visa', 'is_payed']].apply(lambda row: name_from_row(row), axis=1)
        df_statue = df_statue[['name', 'montant_ht']].rename(columns={'montant_ht': 'value'})

        d_control_data['repstatue'] = {
            'plot': {'k': 'pie', 'd': df_statue, 'o': {'hover': True}},
            'rows': [('title', [{'content': 'title', 'value': 'Repartition des factures', 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
                }

        # Load table manager
        table_man = TableLoader(Facture.l_index, Facture.l_fields())

        # App 2 table of bill waiting for mandat
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[df.is_visa == 'no'])

        d_control_data['tablenomandat'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'nothing'},
            'rows': [('title', [{'content': 'title', 'value': 'Facture en attente de visa', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 1
                }
        # App 3 table of bill waiting for payment
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[(df.is_visa == 'yes') & (df.is_payed == 'no')])

        d_control_data['tablenopayement'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'visa'},
            'rows': [('title', [{'content': 'title', 'value': 'Facture en attente de paiement', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 2
                }

        # App 4 table of bill payed
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[df.is_payed == 'yes'])

        d_control_data['tablepayment'] = {
            'table': {'df': df_, 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'payement'},
            'rows': [('title', [{'content': 'title', 'value': 'Facture encaisse', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 3
                }

        return d_control_data


def name_from_row(row):
    if row['is_visa'] == 'yes' and row['is_payed'] == 'no':
        return 'Mandate'

    elif row['is_visa'] == 'yes' and row['is_payed'] == 'yes':
        return 'Encaisse'

    else:
        return 'En attente de mandat'
