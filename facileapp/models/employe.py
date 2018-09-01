# Global imports
import os
import pandas as pd

# Local import
import settings
from facile.core.fields import StringFields, DateFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel


class Employe(BaseModel):

    path = os.path.join(settings.facile_project_path, 'employe.csv')
    l_index = [StringFields(title='Prenom', name='prenom', show_in_table=True, rank=0),
               StringFields(title='Nom', name='nom', show_in_table=True, rank=1)]
    l_actions = map(lambda x: (x.format('un employe'), x.format('un employe')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields():
        l_fields = \
            [StringFields(title='N securite social', name='securite_social'),
             StringFields(title='Carte de sejour', name='carte_sejoure'),
             StringFields(title='Emploi', name='emploie', l_choices=Employe.list('emploi'), show_in_table=True, rank=2),
             StringFields(title='Adresse', name='adresse'),
             StringFields(title='Ville', name='ville'),
             StringFields(title='Code postal', name='code_postal'),
             StringFields(title='tel', name='num_tel'),
             StringFields(title='E-mail', name='mail'),
             StringFields(title="Numero d'entre", name='num_entre'),
             StringFields(title='Qualification', name='qualification'),
             DateFields(title="date d'entre", name='date_start', show_in_table=True, rank=3),
             DateFields(title='date de sortie', name='date_end', show_in_table=True, rank=4),
             ]

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'emploi':
            return [('administration', 'administration'), ('charge affaire', 'charge affaire'),
                    ('charge etude', 'charge etude')]
        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Employe.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Employe(d_index, s.loc[[f.name for f in Employe.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Employe.path

        l_fields = Employe.l_index + Employe.l_fields() + Employe.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_employes(path=None, sep=' ', **kwargs):
        df = Employe.load_db(path)

        for k, v in kwargs.items():
            df = df.loc[df[k] == v]

        return df[['prenom', 'nom']]\
            .apply(lambda r: ('{}' + sep + '{}').format(*[r[c] for c in r.index]), axis=1)\
            .unique()

    @staticmethod
    def form_rendering(step, index=None, data=None):

        if index is not None:
            l_index = [sch.name for sch in Employe.l_index]
            d_index = {k: v for k, v in zip(l_index, index.split('-'))}
        else:
            d_index = None

        form_man = FormManager(Employe.l_index, Employe.l_fields())

        if step % Employe.nb_step_form == 0:
            index_node = StringFields(title='Nom complet', name='index', missing=unicode(''),
                                      l_choices=zip(Employe.get_employes(sep='-'), Employe.get_employes()),
                                      desc="En cas de modification choisir un employe")
            form_man.render_init_form(Employe.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Employe.from_index_(d_index).__dict__

            form_man.render(step % Employe.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_rendering():
        # Load database
        df = Employe.load_db()

        # Sort dataframe by date of maj or creation
        df['sort_key'] = df[[f.name for f in Employe.l_hfields]]\
            .apply(lambda row: max([pd.Timestamp(row[f.name]) for f in Employe.l_hfields if row[f.name] != 'None']),
                   axis=1)
        df = df.sort_values(by='sort_key').reset_index(drop=True)

        # Get columns to display
        l_cols = sorted([(f.name, f.rank) for f in Employe.l_index + Employe.l_fields() if f.show_in_table],
                        key=lambda t: t[1])

        df = df.loc[:10, [t[0] for t in l_cols]]

        return df
