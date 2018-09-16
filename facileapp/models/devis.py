# Global imports
import os
import pandas as pd
from deform.widget import MoneyInputWidget, HiddenWidget, TextInputWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields, DateFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.chantier import Chantier
from facileapp.models.employe import Employe
from facileapp.models.base_prix import Base_prix


class Devis(BaseModel):

    path = os.path.join(settings.facile_project_path, 'devis.csv')

    l_index = [IntegerFields(title='Numero de devis', name='devis_id', widget=HiddenWidget(), table_reduce=True,
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
                 IntegerFields(title='Contact', name='contact_id', l_choices=Devis.list('contact')),
                 IntegerFields(title='Chantier', name='chantier_id', l_choices=Devis.list('chantier')),
                 StringFields(title='Responsable', name='responsable', l_choices=Devis.list('responsable'),
                              table_reduce=True, rank=2),
                 IntegerFields(title="Nombre d'heure BE", name='heure_be', l_choices=zip(range(9000), range(9000))),
                 IntegerFields(title="Nombre d'heure Ch", name='heure_ch', l_choices=zip(range(1000), range(1000))),
                 FloatFields(title='Montant achat', name='montant_achat'),
                 FloatFields(title='Coefficient achat', name='coef_achat'),
                 DateFields(title='Date de debut', name='date_start'),
                 DateFields(title='Date de fin', name='date_end'),
                 StringFields(title='Base de prix', name='base_prix', l_choices=Devis.list('base_prix')),
                 FloatFields(title='Prix', name='price', round=2,
                             table_reduce=True, rank=3)]
        else:
            l_fields = \
                [StringFields(title='Client', name='rs_client', table_reduce=True, rank=1),
                 IntegerFields(title='Contact', name='contact_id'),
                 IntegerFields(title='Chantier', name='chantier_id'),
                 StringFields(title='Responsable', name='responsable', table_reduce=True, rank=2),
                 IntegerFields(title="Nombre d'heure BE", name='heure_be'),
                 IntegerFields(title="Nombre d'heure Ch", name='heure_ch'),
                 FloatFields(title='Montant achat', name='montant_achat'),
                 FloatFields(title='Coefficient achat', name='coef_achat'),
                 DateFields(title='Date de debut', name='date_start'),
                 DateFields(title='Date de fin', name='date_end'),
                 StringFields(title='Base de prix', name='base_prix'),
                 FloatFields(title='Prix', name='price', round=2, table_reduce=True, rank=3)]

        return l_fields

    @staticmethod
    def list(kw):

        if kw == 'client':
            return zip(Client.get_clients(), Client.get_clients())
        elif kw == 'contact':
            return Contact.get_contact('client', return_id=True)
        elif kw == 'chantier':
            return Chantier.get_chantier(return_id=True)
        elif kw == 'responsable':
            return zip(Employe.get_employes(**{'qualification': 'charge affaire'}),
                       Employe.get_employes(**{'qualification': 'charge affaire'}))
        elif kw == 'base_prix':
            return Base_prix.list('base')
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

        if self.devis_id == -1 or self.devis_id is None:
            self.devis_id = df.devis_id.apply(lambda x: int(x)).max() + 1

        self.price = Devis.compute_price({'be': self.__getattribute__('heure_be'),
                                          'ch': self.__getattribute__('heure_ch')},
                                         self.__getattribute__('base_prix'), self.__getattribute__('coef_achat'),
                                         self.__getattribute__('montant_achat'))

        # Try to add and reset conatct id if failed
        try:
            super(Devis, self).add()

        except ValueError, e:
            self.devis_id = devis_id_
            raise ValueError(e.message)

    def alter(self):
        self.price = Devis.compute_price({'be': self.__getattribute__('heure_be'),
                                          'ch': self.__getattribute__('heure_ch')},
                                         self.__getattribute__('base_prix'), self.__getattribute__('coef_achat'),
                                         self.__getattribute__('montant_achat'))
        super(Devis, self).alter()

    @staticmethod
    def compute_price(d_heures, base_prix, coef_achat, montant_achat):
        # Get price from base
        d_prices = Base_prix.get_price(base_prix)

        # Compute price
        price = montant_achat * coef_achat
        price += sum([d_heures[k.split('_')[-1]] * v for k, v in d_prices.items()])

        return price

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Devis.l_index[0].name: Devis.l_index[0].type(index)}
        else:
            d_index = None

        if step % Devis.nb_step_form == 2:

            price = Devis.compute_price({'be': int(data.get('heure_be', 0)), 'ch': int(data.get('heure_ch', 0))},
                                        data.get('base_prix', 'Janvier 2018'), float(data.get('coef_achat', 1)),
                                        float(data.get('montant_achat', 0)))

            data.update({k: v for k, v in Base_prix.get_price(data.get('base_prix', 'Janvier 2018')).items() +
                        [('price', price)]})

            l_fields = [
                FloatFields(title="Prix heure Ch", name='prix_heure_ch', round=2),
                FloatFields(title="Prix heure Ch", name='prix_heure_be', round=2)
            ] + Devis.l_fields(widget=True)

        else:
            l_fields = Devis.l_fields(widget=True)

        form_man = FormLoader(Devis.l_index, l_fields)

        if step % Devis.nb_step_form == 0:
            index_node = IntegerFields(title='Numero de devis', name='index', missing=-1,
                                       l_choices=zip(Devis.get_devis(), Devis.get_devis()),
                                       desc="En cas de modification choisir un numero de devis",)
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

        # App 2 amount of digned affaire by charge d'aff
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