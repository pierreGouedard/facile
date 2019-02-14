# Global imports
import os
import pandas as pd

# Local import
import settings
from facile.core.fields import StringFields, DateFields
from facile.core.form_loader import FormLoader
from facile.core.base_model import BaseModel
from facile.core.table_loader import TableLoader


class Employe(BaseModel):

    path = os.path.join(settings.facile_project_path, 'employe.csv')
    l_index = [StringFields(title='Prenom', name='prenom', table_reduce=True, rank=0),
               StringFields(title='Nom', name='nom', table_reduce=True, rank=1)]
    l_actions = map(lambda x: (x.format('un employe'), x.format('un employe')), BaseModel.l_actions)
    l_documents = [('convoc', 'Lettre de convocation'), ('miseap', 'Lettre de mise a pied')]
    l_apps = ['repqual', 'repemp']
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        l_fields = \
            [StringFields(title='N securite social', name='securite_social'),
             StringFields(title='Carte de sejour', name='carte_sejoure'),
             StringFields(title='Emploie', name='emploie', table_reduce=True, rank=2),
             StringFields(title='Categorie', name='categorie', table_reduce=True, rank=3),
             StringFields(title='Type de contrat', name='type_contrat', table_reduce=True, rank=4),
             StringFields(title='Adresse', name='adresse'),
             StringFields(title='Ville', name='ville'),
             StringFields(title='Code postal', name='code_postal'),
             StringFields(title='tel', name='num_tel'),
             StringFields(title='E-mail', name='mail'),
             DateFields(title="date d'entre", name='date_start', table_reduce=True, rank=5),
             DateFields(title='date de sortie', name='date_end', missing='1970-01-01'),
             ]
        if widget:
            l_fields[3] = StringFields(
                title='Categorie', name='categorie', l_choices=Employe.list('categorie'), table_reduce=True, rank=3
            )
            l_fields[4] = StringFields(
                title='Type de contrat', name='type_contrat', l_choices=Employe.list('type_contrat'), table_reduce=True,
                rank=4
            )

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'categorie':
            return [('administration', 'Administration'), ('charge affaire', "Charge d'affaire"),
                    ('charge etude', "Charge d'etude"), ('chantier', 'Personel chantier')]
        elif kw == 'type_contrat':
            return [('cdi', 'CDI'), ('cdd', "CDD"), ('stagiaire', 'Stagiaire')]
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

        if df.empty:
            return []

        for k, v in kwargs.items():
            df = df.loc[df[k] == v]

        return df[['prenom', 'nom']]\
            .apply(lambda r: ('{}' + sep + '{}').format(*[r[c] for c in r.index]), axis=1)\
            .unique()

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            l_index = [sch.name for sch in Employe.l_index]
            d_index = {k: v for k, v in zip(l_index, index.split('-'))}
        else:
            d_index = None

        form_man = FormLoader(Employe.l_index, Employe.l_fields(widget=True))

        if step % Employe.nb_step_form == 0:
            index_node = StringFields(
                title='Nom complet', name='index', missing=unicode(''),
                l_choices=zip(Employe.get_employes(sep='-'), Employe.get_employes()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un employe"
            )
            form_man.load_init_form(Employe.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Employe.from_index_(d_index).__dict__

            form_man.load(step % Employe.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Employe.load_db()

        # Instantiate table manager
        table_man = TableLoader(Employe.l_index, Employe.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Employe.l_index, Employe.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Employe.load_db()

        # App 1 repartition qualification among employes
        df_qual = df[['prenom', 'qualification']].groupby('qualification')\
            .count()\
            .reset_index()\
            .rename(columns={'qualification': 'name', 'prenom': 'value'})

        d_control_data['repqual'] = {
            'plot': {'k': 'pie', 'd': df_qual, 'o': {'hover': True}},
            'rows': [('title', [{'content': 'title', 'value': 'Repartition des qualifications', 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
                }

        df_empl = df[['prenom', 'emploie']].groupby('emploie')\
            .count()\
            .reset_index()\
            .rename(columns={'emploie': 'name', 'prenom': 'value'})

        # App 2 repartition emploie among employes
        d_control_data['repempl'] = {
            'plot': {'k': 'pie', 'd': df_empl, 'o': {'hover': True}},
            'rows': [('title', [{'content': 'title', 'value': 'Repartition des emploie', 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 1
                }

        return d_control_data
