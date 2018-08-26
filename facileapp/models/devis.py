# Global imports
import os
import pandas as pd
from deform.widget import MoneyInputWidget, HiddenWidget, TextInputWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields, DateFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel


class Devis(BaseModel):

    path = os.path.join(settings.facile_project_path, 'devis.csv')

    d_list = {'action': [('Ajouter un devis', 'Ajouter un devis'),
                         ('Modifier un devis', 'Modifier un devis'),
                         ('Suprimer un devis', 'Suprimer un devis')],

              'client': zip(Client.load_db()['raison_social'].unique(),
                            Client.load_db()['raison_social'].unique()),

              'contact': Contact.get_contact('client', return_id=True),

              'base_prix': Base_prix.d_list['base'],

              'responsable': zip(Employe.get_employes(**{'emploie': 'charge affaire'}),
                                 Employe.get_employes(**{'emploie': 'charge affaire'})),

              'affaire': [(-1, 'NA')] + zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
              }

    l_index = [IntegerFields(title='Numero de devis', name='devis_id', widget=HiddenWidget())]

    l_fields = [IntegerFields(title="Numero d'affaire", name='affaire_id', l_choices=d_list['affaire']),
                StringFields(title='Client', name='rs_client', l_choices=d_list['client']),
                IntegerFields(title='Contact', name='contact_id', l_choices=d_list['contact']),
                StringFields(title='Responsable', name='responsable', l_choices=d_list['responsable']),
                IntegerFields(title="Nombre d'heure BE", name='heure_be'),
                IntegerFields(title="Nombre d'heure Ch", name='heure_ch'),
                FloatFields(title='Montant achat', name='montant_achat'),
                FloatFields(title='Coefficient achat', name='coef_achat'),
                DateFields(title='Date de debut', name='date_start'),
                DateFields(title='Date de fin', name='date_end'),
                StringFields(title='Base de prix', name='base_prix', l_choices=d_list['base_prix']),
                FloatFields(title='Prix', name='price', widget=MoneyInputWidget(readonly=True), round=2)]

    action_field = StringFields(title='Action', name='action', l_choices=d_list['action'], round=0)
    nb_step_form = 3

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Devis.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Devis(d_index, s.loc[[f.name for f in Devis.l_fields]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Devis.path

        return pd.read_csv(path, dtype={f.name: f.type for f in Devis.l_index + Devis.l_fields + Devis.l_hfields}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in Devis.l_index + Devis.l_fields + Devis.l_hfields})

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
    def form_rendering(step, d_index=None, data=None):

        if step % Devis.nb_step_form == 2:

            price = Devis.compute_price({'be': int(data.get('heure_be', 0)), 'ch': int(data.get('heure_ch', 0))},
                                        data.get('base_prix', 'Janvier 2018'), float(data.get('coef_achat', 1)),
                                        float(data.get('montant_achat', 0)))

            data.update({k: v for k, v in Base_prix.get_price(data.get('base_prix', 'Janvier 2018')).items() +
                         [('price', price)]})

            l_fields = [
                FloatFields(title="Prix heure Ch", name='prix_heure_ch', round=2, widget=TextInputWidget(readonly=True)),
                FloatFields(title="Prix heure Ch", name='prix_heure_be', round=2, widget=TextInputWidget(readonly=True))
            ] + Devis.l_fields

        else:
            l_fields = Devis.l_fields

        form_man = FormManager(Devis.l_index, l_fields)

        if step % Devis.nb_step_form == 0:
            index_node = StringFields(title='Nom complet', name='index', missing=unicode(''),
                                      l_choices=zip(Devis.get_devis(), Devis.get_devis()),
                                      desc="En cas de modification choisir un numero de devis",)
            form_man.render_init_form(Devis.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Devis.from_index_(d_index).__dict__

            form_man.render(step % Devis.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data
