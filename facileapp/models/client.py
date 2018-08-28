# Global imports
import os
import pandas as pd

# Local import
import settings
from facile.core.fields import StringFields
from facile.core.form_processor import FormManager
from facile.core.base_model import BaseModel


class Client(BaseModel):

    path = os.path.join(settings.facile_project_path, 'client.csv')
    l_index = [StringFields(title='Raison social', name='raison_social')]
    l_actions = map(lambda x: (x.format('un client'), x.format('un client')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields():
        l_fields = \
            [StringFields(title='contact (financier)', name='contact'),
             StringFields(title='Adresse (financier)', name='adresse'),
             StringFields(title='Ville (financier)', name='ville'),
             StringFields(title='Code postal (financier)', name='code_postal'),
             StringFields(title='tel (financier)', name='num_tel'),
             StringFields(title='E-mail (financier)', name='mail')]

        return l_fields

    @staticmethod
    def list(kw):
        return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Client.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Client(d_index, s.loc[[f.name for f in Client.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Client.path

        l_fields = Client.l_index + Client.l_fields() + Client.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_clients(path=None):
        return Client.load_db(path)['raison_social'].unique()

    @staticmethod
    def form_rendering(step, index=None, data=None):

        if index is not None:
            d_index = {Client.l_index[0].name: index}
        else:
            d_index = None

        form_man = FormManager(Client.l_index, Client.l_fields())

        if step % Client.nb_step_form == 0:
            index_node = StringFields(title='Nom complet', name='index', missing=unicode(''),
                                      l_choices=zip(Client.get_clients(), Client.get_clients()),
                                      desc="En cas de modification choisir un client")
            form_man.render_init_form(Client.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Client.from_index_(d_index).__dict__

            form_man.render(step % Client.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

