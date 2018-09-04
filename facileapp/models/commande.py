# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, FloatFields
from facile.core.form_processor import FormManager
from facile.core.table_processor import TableManager
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.chantier import Chantier
from facileapp.models.employe import Employe
from facileapp.models.fournisseur import Fournisseur


class Commande(BaseModel):

    path = os.path.join(settings.facile_project_path, 'commande.csv')
    l_index = [IntegerFields(title='Numero de Commande', name='commande_id', widget=HiddenWidget(), table_reduce=True,
                             rank=0)]
    l_documents = [('comande', 'Resume de Commande')]
    l_actions = map(lambda x: (x.format('une commande'), x.format('une commande')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields():
        l_fields = \
            [IntegerFields(title="Numero d'affaire", name='affaire_id', l_choices=Commande.list('affaire'),
                           table_reduce=True, rank=1),
             StringFields(title='Fournisseur', name='rs_fournisseur', l_choices=Commande.list('fournisseur'),
                          table_reduce=True, rank=2),
             IntegerFields(title='Chantier', name='chantier_id', l_choices=Commande.list('chantier')),
             StringFields(title='Responsable reception', name='responsable', l_choices=Commande.list('employe')),
             FloatFields(title='Montant Commande HT', name='montant_ht'),
             FloatFields(title='Taux TVA', name='taux_tva', l_choices=Commande.list('tva')),
             FloatFields(title='Montant TVA', name='montant_tva', widget=HiddenWidget()),
             FloatFields(title='Montant TTC', name='montant_ttc', widget=HiddenWidget(), table_reduce=True, rank=3),
             IntegerFields(title="Nombre d'article", name='nb_article', table_reduce=True, rank=4),
             StringFields(title="Liste des articles", name='l_article'),
             StringFields(title='Mandat', name='is_mandated',
                          widget=RadioChoiceWidget(values=Commande.list('statue'), **{'key': 'is_mandated'})),
             StringFields(title='Paiement', name='is_payed',
                          widget=RadioChoiceWidget(values=Commande.list('statue'), **{'key': 'is_payed'}))]

        return l_fields

    @staticmethod
    def list(kw):

        if kw == 'fournisseur':
            return zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs())
        elif kw == 'chantier':
            return Chantier.get_chantier(return_id=True)
        elif kw == 'employe':
            return zip(Employe.get_employes(), Employe.get_employes())
        elif kw == 'affaire':
            return zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
        elif kw == 'statue':
            return [('oui', 'Oui'), ('non', 'Non')]
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

        if self.commande_id == -1 or self.commande_id is None:
            self.commande_id = df.commande_id.apply(lambda x: int(x)).max() + 1

        self.montant_ttc, self.montant_tva = Commande.get_montant(self.__getattribute__('montant_ht'),
                                                                  self.__getattribute__('taux_tva'))

        # Try to add and reset conatct id if failed
        try:
            super(Commande, self).add()

        except ValueError, e:
            self.commande_id = commande_id_
            raise ValueError(e.message)

    def alter(self):

        self.montant_ttc, self.montant_tva = Commande.get_montant(self.__getattribute__('montant_ht'),
                                                                  self.__getattribute__('taux_tva'))

        super(Commande, self).alter()

    @staticmethod
    def get_montant(montant_ht, taux_tva):
        montant_tva = taux_tva * montant_ht
        return montant_tva + montant_ht, montant_tva

    @staticmethod
    def form_rendering(step, index=None, data=None):

        if index is not None:
            d_index = {Commande.l_index[0].name: Commande.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormManager(Commande.l_index, Commande.l_fields())

        if step % Commande.nb_step_form == 0:
            index_node = IntegerFields(title='Numero de commande', name='index', missing=-1,
                                       l_choices=zip(Commande.get_commande(), Commande.get_commande()),
                                       desc="En cas de modification choisir un numero de commande",)
            form_man.render_init_form(Commande.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Commande.from_index_(d_index).__dict__

            form_man.render(step % Commande.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_rendering(reduced=True):
        # Load database
        df = Commande.load_db()

        if reduced:
            table_man = TableManager(Commande.l_index, Commande.l_fields(), limit=10)
            df, kwargs = table_man.render_reduce_table(df)
            d_footer = None
        else:
            table_man = TableManager(Commande.l_index, Commande.l_fields())
            df, d_footer, kwargs = table_man.render_full_table(df)

        df = pd.concat([df.copy() for _ in range(9)], ignore_index=True)
        return df, d_footer, kwargs

    @staticmethod
    def form_document_rendering():

        index_node = StringFields(
            title='Numero de commande', name='index', l_choices=zip(Commande.get_commande(), Commande.get_commande())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Commande.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}