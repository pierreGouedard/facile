# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.client import Client
from facileapp.models.employe import Employe


class Facture(BaseModel):

    path = os.path.join(settings.facile_project_path, 'facture.csv')
    l_index = [IntegerFields(title='Numero de Facture', name='facture_id', widget=HiddenWidget(), table_reduce=True,
                             rank=0)]
    l_documents = [('facture', 'Facture'), ('relance1', 'Lettre de relance 1'), ('relance2', 'Lettre de relance 2'),
                   ('relance3', 'Lettre de relance 3'), ('misede', 'Lettre de mise en demeure')]
    l_actions = map(lambda x: (x.format('une facture'), x.format('une facture')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [IntegerFields(title="Numero d'affaire", name='affaire_id', l_choices=Facture.list('affaire'),
                               table_reduce=True, rank=1),
                 StringFields(title='Client', name='rs_client', l_choices=Facture.list('client'), table_reduce=True,
                              rank=2),
                 StringFields(title='Responsable', name='responsable', l_choices=Facture.list('responsable'),
                              table_reduce=True, rank=3),
                 StringFields(title='Objet', name='objet'),
                 FloatFields(title='Montant facture HT', name='montant_ht'),
                 FloatFields(title='Taux TVA', name='taux_tva', l_choices=Facture.list('tva')),
                 FloatFields(title='Montant TVA', name='montant_tva', widget=HiddenWidget()),
                 FloatFields(title='Montant TTC', name='montant_ttc', widget=HiddenWidget(), table_reduce=True, rank=4),
                 IntegerFields(title='Delai de paiement', name='delai_paiement', l_choices=Facture.list('delai')),
                 StringFields(title='Mandat', name='is_mandated',
                              widget=RadioChoiceWidget(values=Facture.list('statue'), **{'key': 'is_mandated'})),
                 StringFields(title='Encaissement', name='is_payed',
                              widget=RadioChoiceWidget(values=Facture.list('statue'), **{'key': 'is_payed'}))]
        else:
            l_fields = \
                [IntegerFields(title="Numero d'affaire", name='affaire_id', table_reduce=True, rank=1),
                 StringFields(title='Client', name='rs_client', table_reduce=True, rank=2),
                 StringFields(title='Responsable', name='responsable', table_reduce=True, rank=3),
                 StringFields(title='Objet', name='objet'),
                 FloatFields(title='Montant facture HT', name='montant_ht'),
                 FloatFields(title='Taux TVA', name='taux_tva'),
                 FloatFields(title='Montant TVA', name='montant_tva'),
                 FloatFields(title='Montant TTC', name='montant_ttc', table_reduce=True, rank=4),
                 IntegerFields(title='Delai de paiement', name='delai_paiement'),
                 StringFields(title='Mandat', name='is_mandated'),
                 StringFields(title='Encaissement', name='is_payed')]

        return l_fields

    @staticmethod
    def list(kw):

        if kw == 'client':
            return zip(Client.get_clients(), Client.get_clients())
        elif kw == 'responsable':
            return zip(Employe.get_employes(**{'qualification': 'charge affaire'}),
                       Employe.get_employes(**{'qualification': 'charge affaire'}))
        elif kw == 'affaire':
            return zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
        elif kw == 'statue':
            return [('oui', 'Oui'), ('non', 'Non')]
        elif kw == 'delai':
            return [(i, '{} mois'.format(i)) for i in range(12)]
        elif kw == 'tva':
            return [(0.2, '20%'), (0.1, '10%'), (0.055, '5,5%'), (0.021, '2,1%')]
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

        # Save current contact id
        facture_id_ = self.facture_id

        if self.facture_id == -1 or self.facture_id is None:
            self.facture_id = df.facture_id.apply(lambda x: int(x)).max() + 1

        self.montant_ttc, self.montant_tva = Facture.get_montant(self.__getattribute__('montant_ht'),
                                                                 self.__getattribute__('taux_tva'))

        # Try to add and reset conatct id if failed
        try:
            super(Facture, self).add()

        except ValueError, e:
            self.facture_id = facture_id_
            raise ValueError(e.message)

    def alter(self):

        self.montant_ttc, self.montant_tva = Facture.get_montant(self.__getattribute__('montant_ht'),
                                                                 self.__getattribute__('taux_tva'))

        super(Facture, self).alter()

    @staticmethod
    def get_montant(montant_ht, taux_tva):
        montant_tva = taux_tva * montant_ht
        return montant_tva + montant_ht, montant_tva

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Facture.l_index[0].name: Facture.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormLoader(Facture.l_index, Facture.l_fields(widget=True))

        if step % Facture.nb_step_form == 0:
            index_node = IntegerFields(title='Numero de facture', name='index', missing=-1,
                                       l_choices=zip(Facture.get_facture(), Facture.get_facture()),
                                       desc="En cas de modification choisir un numero de facture",)
            form_man.load_init_form(Facture.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Facture.from_index_(d_index).__dict__

            form_man.load(step % Facture.nb_step_form, data_db=data_db, data_form=data)

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
    def form_document_loading():

        index_node = StringFields(
            title='Numero de facture', name='index', l_choices=zip(Facture.get_facture(), Facture.get_facture())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Facture.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Facture.load_db()

        # get dates of current and past business year
        # business_year = dates.get_business_year_from_date(pd.Timestamp.now())
        # date_cur = dates.get_bound_from_business_year(business_year)
        # date_pas = dates.get_bound_from_business_year(business_year - 1)

        # App 1 repartition bill waiting for mandat, waiting for payment, payed for current business year
        df_statue = df[['is_mandated', 'is_payed', 'montant_ttc']].groupby(['is_mandated', 'is_payed'])\
            .sum()\
            .reset_index()
        df_statue['name'] = df_statue[['is_mandated', 'is_payed']].apply(lambda row: name_from_row(row), axis=1)
        df_statue = df_statue[['name', 'montant_ttc']].rename(columns={'montant_ttc': 'value'})

        d_control_data['repstatue'] = {
            'plot': {'k': 'pie', 'd': df_statue, 'o': {'hover': True}},
            'rows': [('title', [{'content': 'title', 'value': 'Repartition des facture', 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
                }

        # Load table manager
        table_man = TableLoader(Facture.l_index, Facture.l_fields())

        # App 2 table of bill waiting for mandat
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[df.is_mandated == 'no'])

        d_control_data['tablenomandat'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'nothing'},
            'rows': [('title', [{'content': 'title', 'value': 'Facture en attente de mandat', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 1
                }
        # App 3 table of bill waiting for payment
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[(df.is_mandated == 'yes') & (df.is_payed == 'no')])

        d_control_data['tablenopayement'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'mandat'},
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
    if row['is_mandated'] == 'yes' and row['is_payed'] == 'no':
        return 'Mandate'

    elif row['is_mandated'] == 'yes' and row['is_payed'] == 'yes':
        return 'Encaisse'

    else:
        return 'En attente de mandat'
