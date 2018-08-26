# Global imports
import os
import pandas as pd
from deform.widget import RadioChoiceWidget, HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel


class Chantier(BaseModel):

    path = os.path.join(settings.facile_project_path, 'chantier.csv')

    d_list = {'client': zip(Client.load_db()['raison_social'].unique(),
                            Client.load_db()['raison_social'].unique()),

              'contact': Contact.get_contact('client', return_id=True),

              'responsable': zip(Employe.get_employes(**{'emploie': 'charge affaire'}),
                                 Employe.get_employes(**{'emploie': 'charge affaire'})),

              'is_active': [('oui', 'Oui'),
                            ('non', 'Non')],

              'action': [('Ajouter un chantier', 'Ajouter un chantier'),
                         ('Modifier un chantier', 'Modifier un chantier'),
                         ('Suprimer un chantier', 'Suprimer un chantier')]}

    l_index = [IntegerFields(title='ID', name='chantier_id', widget=HiddenWidget())]

    l_fields = [StringFields(title='Raison social du client', name='rs_client', l_choices=d_list['client']),
                StringFields(title='Nom du chantier', name='nom'),
                IntegerFields(title='Contact exterieur', name='contact_id', l_choices=d_list['contact']),
                StringFields(title='Responsable du chantier', name='responsable', l_choices=d_list['responsable']),
                StringFields(title='Adresse', name='adresse'),
                StringFields(title='Ville', name='ville'),
                StringFields(title='Code postal', name='code_postal'),
                StringFields(title='Le chantier est actif', name='is_active',
                             widget=RadioChoiceWidget(values=d_list['is_active'], **{'key': 'is_active'}))
                ]

    l_subindex = [0, 1]
    action_field = StringFields(title='Action', name='action', l_choices=d_list['action'], round=0)
    nb_step_form = 2

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Chantier.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Chantier(d_index, s.loc[[f.name for f in Chantier.l_fields]].to_dict(), path=path)

    @staticmethod
    def from_subindex_(d_subindex, path=None):
        df = Chantier.load_db(path)
        d_index = BaseModel.from_subindex(d_subindex, [f.name for f in Chantier.l_index], df)
        return Chantier.from_index_(d_index, path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Chantier.path
        l_fields = Chantier.l_index + Chantier.l_fields + Chantier.l_hfields
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
    def form_rendering(step, d_index=None, data=None):

        form_man = FormManager(Chantier.l_index, Chantier.l_fields, l_subindex=Chantier.l_subindex, use_subindex=True)

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

