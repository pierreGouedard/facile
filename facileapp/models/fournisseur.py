# Global imports
import os
import pandas as pd

# Local import
import settings
from facile.core.fields import StringFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel


class Fournisseur(BaseModel):

    path = os.path.join(settings.facile_db_path, 'fournisseur.csv')

    l_index = [StringFields(title='Raison sociale', name='raison_social', table_reduce=True, rank=0, required=True)]
    l_actions = map(lambda x: (x.format('un fournisseur'), x.format('un fournisseur')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        l_fields = \
            [StringFields(title='Adresse', name='adresse', required=True),
             StringFields(title='CS/BP', name='cs_bp'),
             StringFields(title='Ville', name='ville', required=True),
             StringFields(title='Code postal', name='code_postal', required=True),
             StringFields(title='tel', name='num_tel', table_reduce=True, rank=2),
             StringFields(title='E-mail', name='mail', table_reduce=True, rank=3)]

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
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Fournisseur.l_index[0].name: index}
        else:
            d_index = None

        form_man = FormLoader(Fournisseur.l_index, Fournisseur.l_fields(widget=True))

        if step % Fournisseur.nb_step_form == 0:
            index_node = StringFields(
                title='Raison social', name='index', missing=unicode(''),
                l_choices=zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un fournisseur")
            form_man.load_init_form(Fournisseur.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Fournisseur.from_index_(d_index).__dict__

            form_man.load(step % Fournisseur.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Fournisseur.load_db()

        # Instantiate table manager
        table_man = TableLoader(Fournisseur.l_index, Fournisseur.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Fournisseur.l_index, Fournisseur.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs
