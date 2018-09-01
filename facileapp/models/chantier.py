# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel, ClassProperty
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.employe import Employe


class Chantier(BaseModel):

    path = os.path.join(settings.facile_project_path, 'chantier.csv')
    l_index = [IntegerFields(title='ID', name='chantier_id', widget=HiddenWidget(), show_in_table=True, rank=0)]
    l_subindex = [0, 1]
    l_actions = map(lambda x: (x.format('un chantier'), x.format('un chantier')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields():
        l_fields = \
            [StringFields(title='Raison social du client', name='rs_client', l_choices=Chantier.list('client'),
                          show_in_table=True, rank=1),
             StringFields(title='Nom du chantier', name='nom', show_in_table=True, rank=2),
             IntegerFields(title='Contact exterieur', name='contact_id', l_choices=Chantier.list('contact')),
             StringFields(title='Responsable du chantier', name='responsable', l_choices=Chantier.list('responsable'),
                          show_in_table=True, rank=0),
             StringFields(title='Adresse', name='adresse'),
             StringFields(title='Ville', name='ville'),
             StringFields(title='Code postal', name='code_postal'),
             StringFields(title='Le chantier est actif', name='is_active',
                          widget=RadioChoiceWidget(values=Chantier.list('is_active'), **{'key': 'is_active'}))
             ]

        return l_fields

    @staticmethod
    def list(kw):
        if kw == 'client':
            return zip(Client.load_db()['raison_social'].unique(), Client.load_db()['raison_social'].unique())

        elif kw == 'contact':
            return Contact.get_contact('client', return_id=True)

        elif kw == 'responsable':
            return zip(Employe.get_employes(**{'emploie': 'charge affaire'}),
                       Employe.get_employes(**{'emploie': 'charge affaire'}))
        elif kw == 'is_active':
            return [('oui', 'Oui'), ('non', 'Non')]

        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Chantier.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Chantier(d_index, s.loc[[f.name for f in Chantier.l_fields()]].to_dict(), path=path)

    @staticmethod
    def from_subindex_(d_subindex, path=None):
        df = Chantier.load_db(path)
        d_index = BaseModel.from_subindex(d_subindex, [f.name for f in Chantier.l_index], df)
        return Chantier.from_index_(d_index, path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Chantier.path
        l_fields = Chantier.l_index + Chantier.l_fields() + Chantier.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_chantier(path=None, return_id=False):

        if return_id:
            l_chantier = Chantier.load_db(path).loc[:, ['rs_client', 'nom']] \
                .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1) \
                .to_dict().items()

        else:
            l_chantier = Chantier.load_db(path).loc[:, ['rs_client', 'nom']]\
                .apply(lambda r: '{} - {}'.format(*[r[c] for c in r.index]), axis=1)\
                .unique()

        return l_chantier

    def add(self):

        df = self.load_db(self.path)

        # Save current contact id
        chantier_id_ = self.chantier_id

        if self.chantier_id == -1 or self.chantier_id is None:
            self.chantier_id = df.chantier_id.apply(lambda x: int(x)).max() + 1

        # Try to add and reset conatct id if failed
        try:
            super(Chantier, self).add()
        except ValueError, e:
            self.chantier_id = chantier_id_
            raise ValueError(e.message)

    @staticmethod
    def form_rendering(step, index=None, data=None):

        if index is not None:
            l_subindex = [Chantier.l_fields()[i].name for i in Contact.l_subindex]
            d_index = {k: v for k, v in zip(l_subindex, index.split(' - '))}
        else:
            d_index = None

        form_man = FormManager(Chantier.l_index, Chantier.l_fields(), l_subindex=Chantier.l_subindex, use_subindex=True)

        if step % Chantier.nb_step_form == 0:
            index_node = StringFields(title='Nom complet', name='index', missing=unicode(''),
                                      l_choices=zip(Chantier.get_chantier(), Chantier.get_chantier()),
                                      desc="En cas de modification choisir un chantier")
            form_man.render_init_form(Chantier.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Chantier.from_subindex_(d_index).__dict__

            form_man.render(step % Chantier.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_rendering():
        # Load database
        df = Chantier.load_db()

        # Sort dataframe by date of maj or creation
        df['sort_key'] = df[[f.name for f in Chantier.l_hfields]]\
            .apply(lambda row: max([pd.Timestamp(row[f.name]) for f in Chantier.l_hfields if row[f.name] != 'None']),
                   axis=1)
        df = df.sort_values(by='sort_key', ascending=False).reset_index(drop=True)

        # Get columns to display
        l_cols = sorted([(f.name, f.rank) for f in Chantier.l_index + Chantier.l_fields() if f.show_in_table],
                        key=lambda t: t[1])

        df = df.loc[:10, [t[0] for t in l_cols]]

        return df