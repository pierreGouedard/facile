# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel


class Affaire(BaseModel):

    path = os.path.join(settings.facile_project_path, 'affaire.csv')

    d_list = {'action': [('Ajouter une affaire', 'Ajouter une affaire'),
                         ('Modifier une affaire', 'Modifier une affaire'),
                         ('Suprimer une affaire', 'Suprimer une affaire')],

              'chantier': Chantier.get_chantier(return_id=True),

              'responsable': zip(Employe.get_employes(**{'emploie': 'charge affaire'}),
                                 Employe.get_employes(**{'emploie': 'charge affaire'}))
              }

    l_index = [IntegerFields(title="Numero d'affaire", name='affaire_id', widget=HiddenWidget())]

    l_fields = [IntegerFields(title='Chantier', name='chantier_id', l_choices=d_list['chantier']),
                StringFields(title='Responsable', name='responsable', l_choices=d_list['responsable'])]

    action_field = StringFields(title='Action', name='action', l_choices=d_list['action'], round=0)
    nb_step_form = 2

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Affaire.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Affaire(d_index, s.loc[[f.name for f in Affaire.l_fields]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Affaire.path
        l_fields = Affaire.l_index + Affaire.l_fields + Affaire.l_hfields

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
    def form_rendering(step, d_index=None, data=None):
        form_man = FormManager(Affaire.l_index, Affaire.l_fields)

        if step % Affaire.nb_step_form == 0:
            index_node = StringFields(title='Nom complet', name='index', missing=unicode(''),
                                      l_choices=zip(Affaire.get_affaire(), Affaire.get_affaire()),
                                      desc="En cas de modification choisir un numero d'affaire",)
            form_man.render_init_form(Affaire.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Affaire.from_index_(d_index).__dict__

            form_man.render(step % Affaire.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data
