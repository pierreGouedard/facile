# Global imports
import os
import pandas as pd
from deform.widget import HiddenWidget

# Local import
import settings
from facile.core.fields import StringFields, IntegerFields, MappingFields, SequenceFields
from facile.core.form_processor import FormManager
from facile.core.table_processor import TableManager
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.employe import Employe


class Heure(BaseModel):

    path = os.path.join(settings.facile_project_path, 'heure.csv')
    l_index = [IntegerFields(title='ID', name='heure_id', widget=HiddenWidget(), missing=-1, table_reduce=True,
                             rank=0)]
    l_groupindex = [0]

    l_actions = [('Editer les heures', 'Editer les heures')]

    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)

    nb_step_form = 2

    @staticmethod
    def l_fields():
        l_fields = \
            [StringFields(title="Semaine", name='semaine', widget=HiddenWidget(), table_reduce=True,
                          rank=1),
             IntegerFields(title="Numero d'affaire", name='affaire_id', l_choices=Heure.list('affaire'),
                           table_reduce=True,  rank=2),
             StringFields(title="Nom de l'employe", name='employe', l_choices=Heure.list('employe'), table_reduce=True,
                          rank=3),
             IntegerFields(title="Nombre d'heure BE", name='nb_heure_be', missing=0, table_reduce=True, rank=4),
             IntegerFields(title="Nombre d'heure CH", name='nb_heure_ch', missing=0, table_reduce=True, rank=5)]

        return l_fields

    @staticmethod
    def sequence_field():
        mapping_heure = MappingFields('Heure', 'heure', 'heure', Heure.l_index + Heure.l_fields())
        sequence_field = SequenceFields('Liste des heures', 'heure', mapping_heure)
        return sequence_field

    @staticmethod
    def list(kw):
        if kw == 'employe':
            return zip(Employe.get_employes(), Employe.get_employes())
        elif kw == 'affaire':
            return zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
        elif kw == 'week':
            t_now = pd.Timestamp.now()
            current_monday = (t_now - pd.Timedelta(days=t_now.weekday())).date()
            l_dates = pd.DatetimeIndex(start=current_monday - pd.Timedelta(days=70),
                                       end=current_monday + pd.Timedelta(days=70),
                                       freq='w')
            return [str((t + pd.Timedelta(days=1)).date()) for t in l_dates]
        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Heure.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Heure(d_index, s.loc[[f.name for f in Heure.l_fields()]].to_dict(), path=path)

    @staticmethod
    def from_groupindex_(d_groupindex, path=None):

        df = Heure.load_db(path)
        l_indices = BaseModel.from_groupindex(d_groupindex, [f.name for f in Heure.l_index], df)

        return [Heure.from_index_(d_index, path=path) for d_index in l_indices]

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Heure.path

        return pd.read_csv(path, dtype={f.name: f.type for f in Heure.l_index + Heure.l_fields() + Heure.l_hfields}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in Heure.l_index + Heure.l_fields() + Heure.l_hfields})

    @staticmethod
    def get_heure(path=None):
        return Heure.load_db(path)['heure_id'].unique()

    @staticmethod
    def get_groupindex(path=None):
        return Heure.load_db(path)['semaine'].unique()

    def add(self):
        df = self.load_db(self.path)

        # Save current contact id
        heure_id_ = self.heure_id

        if self.heure_id == -1 or self.heure_id is None:
            self.heure_id = df.heure_id.apply(lambda x: int(x)).max() + 1

        # Try to add and reset conatct id if failed
        try:
            super(Heure, self).add()

        except ValueError, e:
            self.heure_id = heure_id_
            raise ValueError(e.message)

    def alter(self):
        super(Heure, self).alter()

    @staticmethod
    def form_rendering(step, index=None, data=None):

        d_index = {
            Heure.l_fields()[Heure.l_groupindex[0]].name: Heure.l_fields()[Heure.l_groupindex[0]].type(index)
        }

        form_man = FormManager([], [Heure.sequence_field()], use_groupindex=True)

        if step % Heure.nb_step_form == 0:
            index_node = StringFields(title='Semaine', name='index', missing=-1,
                                      l_choices=zip(Heure.list('week'), Heure.list('week')))
            form_man.render_init_form(Heure.action_field, index_node)

        else:

            l_names = [f.name for f in Heure.l_fields() + Heure.l_index]
            data_db = {
                Heure.sequence_field().name:
                    [{k: v for k, v in h.__dict__.items() if k in l_names} for h in Heure.from_groupindex_(d_index)]
            }

            form_man.render(step % Heure.nb_step_form, data_db=data_db, data_form=data)
        return form_man.d_form_data

    @staticmethod
    def table_rendering(reduced=True):
        # Load database
        df = Heure.load_db()

        if reduced:
            table_man = TableManager(Heure.l_index, Heure.l_fields(), limit=10)
            df, kwargs = table_man.render_reduce_table(df)
            d_footer = None
        else:
            table_man = TableManager(Heure.l_index, Heure.l_fields())
            df, d_footer, kwargs = table_man.render_full_table(df)

        df = pd.concat([df.copy() for _ in range(9)], ignore_index=True)
        return df, d_footer, kwargs