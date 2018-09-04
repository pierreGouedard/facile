# Global imports
import os
import pandas as pd

# Local import
import settings
from facile.core.fields import StringFields
from facile.core.form_processor import FormManager
from facile.core.table_processor import TableManager
from facile.core.base_model import BaseModel


class Fournisseur(BaseModel):

    path = os.path.join(settings.facile_project_path, 'fournisseur.csv')

    l_index = [StringFields(title='Raison social', name='raison_social', table_reduce=True, rank=0)]
    l_actions = map(lambda x: (x.format('un fournisseur'), x.format('un fournisseur')), BaseModel.l_actions)
    l_documents = [('fpay', 'Lettre pour paiement'), ('fmerci', 'Lettre de remerciement')]
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields():
        l_fields = \
            [StringFields(title='contact (financier)', name='contact', table_reduce=True, rank=1),
             StringFields(title='Adresse (financier)', name='adresse'),
             StringFields(title='Ville (financier)', name='ville'),
             StringFields(title='Code postal (financier)', name='code_postal'),
             StringFields(title='tel (financier)', name='num_tel', table_reduce=True, rank=2),
             StringFields(title='E-mail (financier)', name='mail', table_reduce=True, rank=3)]

        return l_fields

    @staticmethod
    def list(kw):
        return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Fournisseur.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Fournisseur(d_index, s.loc[[f.name for f in Fournisseur.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Fournisseur.path

        l_fields = Fournisseur.l_index + Fournisseur.l_fields() + Fournisseur.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_fournisseurs(path=None):
        return Fournisseur.load_db(path)['raison_social'].unique()

    @staticmethod
    def form_rendering(step, index=None, data=None):

        if index is not None:
            d_index = {Fournisseur.l_index[0].name: index}
        else:
            d_index = None

        form_man = FormManager(Fournisseur.l_index, Fournisseur.l_fields())

        if step % Fournisseur.nb_step_form == 0:
            index_node = StringFields(title='Raison social', name='index', missing=unicode(''),
                                      l_choices=zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs()),
                                      desc="En cas de modification choisir un fournisseur")
            form_man.render_init_form(Fournisseur.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Fournisseur.from_index_(d_index).__dict__

            form_man.render(step % Fournisseur.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_rendering(reduced=True):
        # Load database
        df = Fournisseur.load_db()

        if reduced:
            table_man = TableManager(Fournisseur.l_index, Fournisseur.l_fields(), limit=10)
            df, kwargs = table_man.render_reduce_table(df)
            d_footer = None
        else:
            table_man = TableManager(Fournisseur.l_index, Fournisseur.l_fields())
            df, d_footer, kwargs = table_man.render_full_table(df)

        df = pd.concat([df.copy() for _ in range(9)], ignore_index=True)
        return df, d_footer, kwargs

    @staticmethod
    def form_document_rendering():

        index_node = StringFields(
            title='Raison social', name='index', l_choices=zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Fournisseur.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}