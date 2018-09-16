# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.devis import Devis
from facileapp.models.employe import Employe


class Affaire(BaseModel):

    path = os.path.join(settings.facile_project_path, 'affaire.csv')
    l_index = [IntegerFields(title="Numero d'affaire", name='affaire_id', widget=HiddenWidget(), table_reduce=True,
                             rank=0)]
    l_documents = [('ftravaux', 'Feuille de travaux')]
    l_actions = map(lambda x: (x.format('une affaire'), x.format('une affaire')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [IntegerFields(title="Numero de devis", name='devis_id', l_choices=Affaire.list('devis'), table_reduce=True,
                               rank=1),
                StringFields(title='Responsable', name='responsable', l_choices=Affaire.list('responsable'),
                             table_reduce=True, rank=2)]

        else:
            l_fields = \
                [IntegerFields(title="Numero de devis", name='devis_id', table_reduce=True, rank=1),
                StringFields(title='Responsable', name='responsable', table_reduce=True, rank=2)]

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'responsable':
            return zip(Employe.get_employes(**{'qualification': 'charge affaire'}),
                       Employe.get_employes(**{'qualification': 'charge affaire'}))
        elif kw == 'devis':
            return zip(Devis.get_devis(), Devis.get_devis())

        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Affaire.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Affaire(d_index, s.loc[[f.name for f in Affaire.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Affaire.path
        l_fields = Affaire.l_index + Affaire.l_fields() + Affaire.l_hfields

        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_affaire(path=None):
        return Affaire.load_db(path)['affaire_id'].unique()

    def add(self):
        df = self.load_db(self.path)

        # Save current contact id
        affaire_id_ = self.affaire_id

        if self.affaire_id == -1 or self.affaire_id is None:
            self.affaire_id = df.affaire_id.apply(lambda x: int(x)).max() + 1

        # Try to add and reset conatct id if failed
        try:
            super(Affaire, self).add()
        except ValueError, e:
            self.affaire_id = affaire_id_
            raise ValueError(e.message)

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Affaire.l_index[0].name: Affaire.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormLoader(Affaire.l_index, Affaire.l_fields(widget=True))

        if step % Affaire.nb_step_form == 0:
            index_node = IntegerFields(title="Numero d'affaire", name='index', missing=-1,
                                       l_choices=zip(Affaire.get_affaire(), Affaire.get_affaire()),
                                       desc="En cas de modification choisir un numero d'affaire",)
            form_man.load_init_form(Affaire.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Affaire.from_index_(d_index).__dict__

            form_man.load(step % Affaire.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True):
        # Load database
        df = Affaire.load_db()

        if reduced:
            table_man = TableLoader(Affaire.l_index, Affaire.l_fields(), limit=10)
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None
        else:
            l_model_cols = [f.name for f in Affaire.l_index + Affaire.l_fields()]
            table_man = TableLoader(Affaire.l_index, Affaire.l_fields())
            l_extra_cols = [c for c in df.columns if c not in l_model_cols]
            df, d_footer, kwargs = table_man.load_full_table(df, l_extra_cols=l_extra_cols)

        return df, d_footer, kwargs

    @staticmethod
    def form_document_loading():

        index_node = StringFields(
            title="Numero d'affaire", name='index', l_choices=zip(Affaire.get_affaire(), Affaire.get_affaire())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Affaire.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

