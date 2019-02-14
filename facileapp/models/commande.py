# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields, MoneyFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.chantier import Chantier
from facileapp.models.employe import Employe
from facileapp.models.fournisseur import Fournisseur


class Commande(BaseModel):

    path = os.path.join(settings.facile_project_path, 'commande.csv')
    l_index = [StringFields(title='Numero de Commande', name='commande_id', widget=HiddenWidget(), table_reduce=True,
                            rank=0)]
    l_documents = [('comande', 'Resume de Commande')]
    l_actions = map(lambda x: (x.format('une commande'), x.format('une commande')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title="Numero d'affaire", name='affaire_id', l_choices=Commande.list('affaire'),
                              table_reduce=True, rank=1),
                 StringFields(title='Fournisseur', name='raison_social', l_choices=Commande.list('fournisseur'),
                              table_reduce=True, rank=2),
                 MoneyFields(title='Montant Commande HT', name='montant_ht'),
                 FloatFields(title='Taux TVA', name='taux_tva', l_choices=Commande.list('tva')),
                 MoneyFields(title='Montant TVA', name='montant_tva', widget=HiddenWidget()),
                 MoneyFields(title='Montant TTC', name='montant_ttc', widget=HiddenWidget(), table_reduce=True, rank=3),
                 StringFields(title="Liste des articles", name='l_article')]
        else:
            l_fields = \
                [StringFields(title="Numero d'affaire", name='affaire_id', table_reduce=True, rank=1),
                 StringFields(title='Fournisseur', name='raison_social', table_reduce=True, rank=2),
                 MoneyFields(title='Montant Commande HT', name='montant_ht'),
                 FloatFields(title='Taux TVA', name='taux_tva'),
                 MoneyFields(title='Montant TVA', name='montant_tva'),
                 MoneyFields(title='Montant TTC', name='montant_ttc', table_reduce=True, rank=3),
                 StringFields(title="Liste des articles", name='l_article')]

        return l_fields

    @staticmethod
    def list(kw):

        if kw == 'fournisseur':
            return zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs())
        elif kw == 'affaire':
            return zip(Affaire.get_affaire(sep='-'), map(str, Affaire.get_affaire(sep=' - ')))
        elif kw == 'tva':
            return [(0.2, '20%'), (0.1, '10%'), (0.055, '5,5%'), (0.021, '2,1%')]
        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Commande.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Commande(d_index, s.loc[[f.name for f in Commande.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Commande.path

        return pd.read_csv(path, dtype={f.name: f.type for f in Commande.l_index + Commande.l_fields() + Commande.l_hfields}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in Commande.l_index + Commande.l_fields() + Commande.l_hfields})

    @staticmethod
    def get_commande(path=None):
        return Commande.load_db(path)['commande_id'].unique()

    def add(self):
        df = self.load_db(self.path)

        # Save current contact id
        commande_id_ = self.commande_id

        if self.commande_id == '' or self.commande_id is None:
            self.commande_id = 'CM{0:0=4d}'.format(df.commande_id.apply(lambda x: int(x.replace('CM', ''))).max() + 1)

        self.montant_ttc, self.montant_tva = Commande.get_montant(self.__getattribute__('montant_ht'),
                                                                  self.__getattribute__('taux_tva'))

        # Try to add and reset conatct id if failed
        try:
            super(Commande, self).add()

        except ValueError, e:
            self.commande_id = commande_id_
            raise ValueError(e.message)

        return self

    def alter(self):

        self.montant_ttc, self.montant_tva = Commande.get_montant(self.__getattribute__('montant_ht'),
                                                                  self.__getattribute__('taux_tva'))

        super(Commande, self).alter()

        return self

    @staticmethod
    def get_montant(montant_ht, taux_tva):
        montant_tva = taux_tva * montant_ht
        return montant_tva + montant_ht, montant_tva

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Commande.l_index[0].name: Commande.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormLoader(Commande.l_index, Commande.l_fields(widget=True))

        if step % Commande.nb_step_form == 0:
            index_node = StringFields(
                title='Numero de commande', name='index', missing=-1,
                l_choices=zip(Commande.get_commande(), Commande.get_commande()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un numero de commande",
            )
            form_man.load_init_form(Commande.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Commande.from_index_(d_index).__dict__

            form_man.load(step % Commande.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Commande.load_db()
        table_man = TableLoader(Commande.l_index, Commande.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Commande.l_index, Commande.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Commande.load_db()

        # App 1 Commande en cours par affaire
        df_com_aff = df[['affaire_id', 'montant_ttc']].groupby(['affaire_id'])\
            .sum()\
            .reset_index()\
            .rename(columns={'affaire_id': 'label'})

        d_control_data['comaffaire'] = {
            'plot': {'k': 'bar', 'd': df_com_aff, 'o': {'val_col': 'montant_ttc'}},
            'rows': [('title', [{'content': 'title', 'value': "Commande par affaire", 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
        }

        # Load table manager
        table_man = TableLoader(Commande.l_index, Commande.l_fields())

        # App 2 table of command waiting for mandat
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[df.is_visa == 'no'])

        d_control_data['tablenomandat'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'nothing'},
            'rows': [('title', [{'content': 'title', 'value': 'Commande en attente de mandat', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 1
                }
        # App 3 table of command waiting for payment
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[(df.is_visa == 'yes') & (df.is_payed == 'no')])

        d_control_data['tablenopayement'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'visa'},
            'rows': [('title', [{'content': 'title', 'value': 'Commandes a payer', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 2
                }

        # App 4 table of Commande payed
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[df.is_payed == 'yes'])

        d_control_data['tablepayment'] = {
            'table': {'df': df_, 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'payement'},
            'rows': [('title', [{'content': 'title', 'value': 'Commandes payees', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 3
                }

        return d_control_data
