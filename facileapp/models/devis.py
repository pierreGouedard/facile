# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields, DateFields, MoneyFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.employe import Employe


class Devis(BaseModel):

    path = os.path.join(settings.facile_project_path, 'devis.csv')

    l_index = [StringFields(title='Numero de devis', name='devis_id', widget=HiddenWidget(), table_reduce=True,
                            rank=0)]
    l_documents = [('devis', 'Devis')]
    l_actions = map(lambda x: (x.format('un devis'), x.format('un devis')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 3

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title='Client', name='rs_client', l_choices=Devis.list('client'), table_reduce=True,
                              rank=1),
                 StringFields(title='Contact client', name='contact_id', l_choices=Devis.list('contact')),
                 StringFields(title='Responsable devis', name='responsable', l_choices=Devis.list('responsable'),
                              table_reduce=True, rank=2),
                 StringFields(title='Designation devis', name='object'),
                 IntegerFields(title="Heure autre", name='heure_autre', l_choices=zip(range(9000), range(9000))),
                 IntegerFields(title="Heure Production", name='heure_prod', l_choices=zip(range(1000), range(1000))),
                 MoneyFields(title="Prix heure autre", name='prix_heure_autre'),
                 MoneyFields(title="Prix heure Production", name='prix_heure_prod'),
                 MoneyFields(title='Montant achat', name='montant_achat'),
                 FloatFields(title='Coefficient achat', name='coef_achat'),
                 StringFields(title='Base de prix', name='base_prix', l_choices=Devis.list('base_prix')),
                 DateFields(title='Date de debut', name='date_start'),
                 DateFields(title='Date de fin', name='date_end'),
                 MoneyFields(title='Prix', name='price', round=2, table_reduce=True, rank=3)]
        else:
            l_fields = \
                [StringFields(title='Client', name='rs_client', table_reduce=True, rank=1),
                 StringFields(title='Contact client', name='contact_id'),
                 StringFields(title='Responsable devis', name='responsable', table_reduce=True, rank=2),
                 StringFields(title='Designation devis', name='object'),
                 IntegerFields(title="Heure autre", name='heure_autre'),
                 IntegerFields(title="Heure Production", name='heure_prod'),
                 MoneyFields(title="Prix heure autre", name='prix_heure_autre'),
                 MoneyFields(title="Prix heure Production", name='prix_heure_prod'),
                 MoneyFields(title='Montant achat', name='montant_achat'),
                 FloatFields(title='Coefficient achat', name='coef_achat'),
                 StringFields(title='Base de prix', name='base_prix'),
                 DateFields(title='Date de debut', name='date_start'),
                 DateFields(title='Date de fin', name='date_end'),
                 MoneyFields(title='Prix', name='price', round=2, table_reduce=True, rank=3)]

        return l_fields

    @staticmethod
    def list(kw):

        d_month = {
            1: 'Janvier {}', 2: 'Fevrier {}', 3: 'Mars {}', 4: 'Avril {}', 5: 'Mai {}', 6: 'Juin {}', 7: 'Juillet {}',
            8: 'Aout {}', 9: 'Septembre {}', 10: 'Octobre {}', 11: 'Novembre {}', 12: 'Decembre {}'
        }

        if kw == 'client':
            return zip(Client.get_clients(), Client.get_clients())
        elif kw == 'contact':
            return Contact.get_contact('client_commande', return_id=True)
        elif kw == 'responsable':
            return zip(Employe.get_employes(**{'categorie': 'charge affaire'}),
                       Employe.get_employes(**{'categorie': 'charge affaire'}))
        elif kw == 'base_prix':
            d = pd.Timestamp.now().date()
            l_dates = pd.DatetimeIndex(start=d - pd.Timedelta(days=95), end=d + pd.Timedelta(days=95), freq='M')
            return [(d_month[t.month].format(t.year), d_month[t.month].format(t.year)) for t in l_dates]
        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Devis.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Devis(d_index, s.loc[[f.name for f in Devis.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Devis.path

        return pd.read_csv(path, dtype={f.name: f.type for f in Devis.l_index + Devis.l_fields() + Devis.l_hfields}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in Devis.l_index + Devis.l_fields() + Devis.l_hfields})

    @staticmethod
    def get_devis(path=None):
        return Devis.load_db(path)['devis_id'].unique()

    def add(self):
        df = self.load_db(self.path)

        # Save current contact id
        devis_id_ = self.devis_id

        if self.devis_id == '' or self.devis_id is None:
            self.devis_id = 'DV{0:0=4d}'.format(df.devis_id.apply(lambda x: int(x.replace('DV', ''))).max() + 1)

        self.price = Devis.compute_price(
            {'hp': self.__getattribute__('heure_prod'), 'ha': self.__getattribute__('heure_autre'),
             'php': self.__getattribute__('prix_heure_prod'), 'pha':self.__getattribute__('prix_heure_autre')},
            {'ca': self.__getattribute__('coef_achat'), 'ma': self.__getattribute__('montant_achat')}
        )

        # Try to add and reset contact id if failed
        try:
            super(Devis, self).add()

        except ValueError, e:
            self.devis_id = devis_id_
            raise ValueError(e.message)

        return self

    def alter(self):
        self.price = Devis.compute_price(
            {'hp': self.__getattribute__('heure_prod'), 'ha': self.__getattribute__('heure_autre'),
             'php': self.__getattribute__('prix_heure_prod'), 'pha': self.__getattribute__('prix_heure_autre')},
            {'ca': self.__getattribute__('coef_achat'), 'ma': self.__getattribute__('montant_achat')}
        )
        super(Devis, self).alter()

    @staticmethod
    def compute_price(d_heures, d_achats):
        # Compute price
        price = d_achats['ma'] * d_achats['ca'] + d_heures['hp'] * d_heures['php'] + d_heures['ha'] * d_heures['pha']
        return price

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Devis.l_index[0].name: Devis.l_index[0].type(index)}
        else:
            d_index = None

        if step % Devis.nb_step_form == 2:
            # Compute price
            price = Devis.compute_price(
                {'hp': int(data.get('heure_prod', 0)), 'ha': int(data.get('heure_autre', 0)),
                 'php': float(data.get('prix_heure_prod', 0)), 'pha': float(data.get('prix_heure_autre', 0))},
                {'ca': float(data.get('coef_achat', 1)), 'ma': float(data.get('montant_achat', 0))}
            )
            data.update({'price': price})

        form_man = FormLoader(Devis.l_index, Devis.l_fields(widget=True))

        if step % Devis.nb_step_form == 0:
            index_node = StringFields(
                title='Numero de devis', name='index', missing=-1,
                l_choices=zip(Devis.get_devis(), Devis.get_devis()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un numero de devis"
            )
            form_man.load_init_form(Devis.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Devis.from_index_(d_index).__dict__

            form_man.load(step % Devis.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True):
        # Load database
        df = Devis.load_db()

        if reduced:
            table_man = TableLoader(Devis.l_index, Devis.l_fields(), limit=10)
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None
        else:
            table_man = TableLoader(Devis.l_index, Devis.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def form_document_loading():

        index_node = StringFields(
            title='Numero de devis', name='index', l_choices=zip(Devis.get_devis(), Devis.get_devis())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Devis.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Devis.load_db()

        # App 2 amount of signed affaire by charge d'aff
        df_chardaff = df[['responsable', 'price']].groupby('responsable')\
            .sum()\
            .reset_index()\
            .rename(columns={'responsable': 'label'})

        d_control_data['devisresp'] = {
            'plot': {'k': 'bar', 'd': df_chardaff, 'o': {'val_col': 'price'}},
            'rows': [('title', [{'content': 'title', 'value': "Devis envoye par charge d'affaire", 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
        }
        return d_control_data