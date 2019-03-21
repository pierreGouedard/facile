#!/usr/bin/python
# -*- coding: latin-1 -*-

# Global imports
import pandas as pd

# Local import
from facile.core.fields import StringFields, DateFields
from facile.core.form_loader import FormLoader
from facile.core.base_model import BaseModel
from facile.core.table_loader import TableLoader


class Employe(BaseModel):

    table_name = 'employe'
    l_index = [StringFields(title=u'Prénom', name='prenom', table_reduce=True, rank=0, primary_key=True),
               StringFields(title=u'Nom', name='nom', table_reduce=True, rank=1, primary_key=True)]
    l_actions = map(lambda x: (x.format(u'un employe'), x.format(u'un employe')), BaseModel.l_actions)
    l_documents = [('convoc', u'Lettre de convocation'), ('miseap', u'Lettre de mise a pied')]
    l_apps = ['repqual', 'repemp']
    action_field = StringFields(title=u'Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        l_fields = \
            [StringFields(title=u'N sécurité social', name='securite_social', required=True),
             StringFields(title=u'Carte de séjour', name='carte_sejoure', required=False),
             StringFields(title=u'Emploi', name='emploi', table_reduce=True, rank=2, required=True),
             StringFields(title=u'Catégorie', name='categorie', table_reduce=True, rank=3, required=True),
             StringFields(title=u'Type de contrat', name='type_contrat', table_reduce=True, rank=4, required=True),
             StringFields(title=u'Adresse', name='adresse', required=True),
             StringFields(title=u'Ville', name='ville', required=True),
             StringFields(title=u'Code postal', name='code_postal', required=True),
             StringFields(title=u'tel', name='num_tel'),
             StringFields(title=u'E-mail', name='mail'),
             DateFields(title=u"date d'entré", name='date_start', table_reduce=True, rank=5, required=True),
             DateFields(title=u'date de sortie', name='date_end', missing='1970-01-01'),
             ]
        if widget:
            l_fields[3] = StringFields(
                title=u'Catégorie', name='categorie', l_choices=Employe.list('categorie'), table_reduce=True, rank=3
            )
            l_fields[4] = StringFields(
                title=u'Type de contrat', name='type_contrat', l_choices=Employe.list('type_contrat'), table_reduce=True,
                rank=4
            )

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Employe', name=Employe.table_name, dbcols=[f.dbcol() for f in Employe.l_index + Employe.l_fields()]
        )

    @staticmethod
    def list(kw):
        if kw == 'categorie':
            return [(u'administration', u'Administration'), (u'charge affaire', u"Chargé d'affaire"),
                    (u'charge etude', u"Chargé d'étude"), (u'chantier', u'Personel chantier')]
        elif kw == 'type_contrat':
            return [(u'cdi', u'CDI'), (u'cdd', u"CDD"), (u'stagiaire', u'Stagiaire')]
        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('employe', d_index)
        return Employe(d_index, s.loc[[f.name for f in Employe.l_fields()]].to_dict())

    @staticmethod
    def load_db(**kwargs):
        # Get fields
        l_fields = Employe.l_index + Employe.l_fields() + Employe.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='employe', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_employes(sep=' ', **kwargs):

        # Get list of employ name and surname
        df = Employe.driver.select(Employe.table_name, columns=['prenom', 'nom'], **kwargs) \
            .transform({f.name: f.processing_db['download'] for f in Employe.l_index}) \
            .apply(lambda r: (u'{}' + sep + u'{}').format(*[r[c] for c in r.index]), axis=1)

        if df.empty:
            return []

        return df.unique()

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
                title=u'Nom complet', name='index', missing=u'',
                l_choices=zip(Employe.get_employes(sep='-'), Employe.get_employes()) + [(u'new', u'Nouveau')],
                desc=u"En cas de modification choisir un employé"
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

        # App 1 repartition categorie among employes
        df_qual = df[['prenom', 'categorie']].groupby('categorie')\
            .count()\
            .reset_index()\
            .rename(columns={'categorie': 'name', 'prenom': 'value'})
        df_qual['hover'] = df_qual('value')

        d_control_data['repqual'] = {
            'plot': {'k': 'pie', 'd': df_qual, 'o': {'hover': True}},
            'rows': [('title', [{'content': 'title', 'value': u"Répartition des catégories d'employe", 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
                }

        return d_control_data
