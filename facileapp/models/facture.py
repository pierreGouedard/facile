# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget, TextInputWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields, DateFields
from facile.core.form_processor import FormManager
from facile.core.table_processor import TableManager
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.client import Client
from facileapp.models.employe import Employe


class Facture(BaseModel):

    path = os.path.join(settings.facile_project_path, 'facture.csv')
    l_index = [IntegerFields(title='Numero de Facture', name='facture_id', widget=HiddenWidget(), table_reduce=True,
                             rank=0)]
    l_documents = [('facture', 'Facture')]
    l_actions = map(lambda x: (x.format('une facture'), x.format('une facture')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields():
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

        return l_fields

    @staticmethod
    def list(kw):

        if kw == 'client':
            return zip(Client.get_clients(), Client.get_clients())
        elif kw == 'responsable':
            return zip(Employe.get_employes(**{'emploie': 'charge affaire'}),
                       Employe.get_employes(**{'emploie': 'charge affaire'}))
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
    def form_rendering(step, index=None, data=None):

        if index is not None:
            d_index = {Facture.l_index[0].name: Facture.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormManager(Facture.l_index, Facture.l_fields())

        if step % Facture.nb_step_form == 0:
            index_node = IntegerFields(title='Numero de facture', name='index', missing=-1,
                                       l_choices=zip(Facture.get_facture(), Facture.get_facture()),
                                       desc="En cas de modification choisir un numero de facture",)
            form_man.render_init_form(Facture.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Facture.from_index_(d_index).__dict__

            form_man.render(step % Facture.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_rendering(reduced=True):
        # Load database
        df = Facture.load_db()

        if reduced:
            table_man = TableManager(Facture.l_index, Facture.l_fields(), limit=10)
            df, kwargs = table_man.render_reduce_table(df)
            d_footer = None
        else:
            table_man = TableManager(Facture.l_index, Facture.l_fields())
            df, d_footer, kwargs = table_man.render_full_table(df)

        df = pd.concat([df.copy() for _ in range(9)], ignore_index=True)
        return df, d_footer, kwargs

    @staticmethod
    def form_document_rendering():

        index_node = StringFields(
            title='Numero de facture', name='index', l_choices=zip(Facture.get_facture(), Facture.get_facture())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Facture.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}