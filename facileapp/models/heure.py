# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields, IntegerFields, MappingFields, SequenceFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.employe import Employe
from facile.utils import dates


class Heure(BaseModel):

    table_name = 'heure'
    l_index = [IntegerFields(title='ID', name='heure_id', widget=HiddenWidget(), missing=-1, table_reduce=True,
                             rank=0, primary_key=True)]
    l_groupindex = [0]

    l_actions = [('Editer les heures', 'Editer les heures')]

    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)

    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title="Semaine", name='semaine', widget=HiddenWidget(), table_reduce=True,
                              rank=1),
                 StringFields(title="Numero d'affaire", name='affaire_id', l_choices=Heure.list('affaire'),
                              table_reduce=True,  rank=2, required=True),
                 StringFields(title="Designation", name='name', l_choices=Heure.list('employe'), table_reduce=True,
                              rank=3, desc="Choisir 'Interimaires' pour ajouter le cumul des heures des interimaires",
                              required=True),
                 IntegerFields(title="Cumul heure prod", name='heure_prod', l_choices=Heure.list('heures'),
                               missing=0, table_reduce=True, rank=4, required=True),
                 IntegerFields(title="Cumul heure autre", name='heure_autre', l_choices=Heure.list('heures'),
                               missing=0, table_reduce=True, rank=5, required=True)]
        else:
            l_fields = \
                [StringFields(title="Semaine", name='semaine', table_reduce=True, rank=1),
                 StringFields(title="Numero d'affaire", name='affaire_id', table_reduce=True,  rank=2),
                 StringFields(title="designation", name='name', table_reduce=True, rank=3),
                 IntegerFields(title="Cumul heure prod", name='heure_prod', missing=0, table_reduce=True, rank=4),
                 IntegerFields(title="Cumul heure autre", name='heure_autre', missing=0, table_reduce=True, rank=5)]

        return l_fields

    @staticmethod
    def sequence_field():
        mapping_heure = MappingFields('Heure', 'heure', 'heure', Heure.l_index + Heure.l_fields(widget=True))
        sequence_field = SequenceFields('Liste des heures', 'heure', mapping_heure)
        return sequence_field

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Heure', name=Heure.table_name, dbcols=[f.dbcol() for f in Heure.l_index + Heure.l_fields()]
        )

    @staticmethod
    def list(kw):
        if kw == 'employe':
            return zip(Employe.get_employes(), Employe.get_employes()) + [('interim', 'Interimaires')]
        elif kw == 'affaire':
            return zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
        elif kw == 'week':
            current_monday = dates.get_current_start_date()
            l_dates = pd.DatetimeIndex(start=current_monday - pd.Timedelta(days=30),
                                       end=current_monday + pd.Timedelta(days=6),
                                       freq='w')
            return [str((t + pd.Timedelta(days=1)).date()) for t in l_dates]
        elif kw == 'heures':
            return zip(range(1000), range(1000))
        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('heure', d_index)

        return Heure(d_index, s.loc[[f.name for f in Heure.l_fields()]].to_dict())

    @staticmethod
    def from_groupindex_(d_groupindex):
        l_indices = BaseModel.from_groupindex('heure', d_groupindex, [f.name for f in Heure.l_index])

        return [Heure.from_index_(d_index) for d_index in l_indices]

    @staticmethod
    def load_db(**kwargs):
        l_fields = Heure.l_index + Heure.l_fields() + Heure.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='heure', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_heure():
        return Heure.load_db(columns=['heure_id'])['heure_id'].unique()

    @staticmethod
    def get_groupindex():
        return Heure.load_db(columns=['semaine']).unique()

    def add(self):

        l_heures = self.get_heure()

        # Save current contact id
        heure_id_ = self.heure_id

        if self.heure_id == -1 or self.heure_id is None:
            self.heure_id = max(map(int, l_heures)) + 1

        # Try to add and reset conatct id if failed
        try:
            super(Heure, self).add()

        except ValueError, e:
            self.heure_id = heure_id_
            raise ValueError(e.message)

        return self

    @staticmethod
    def form_loading(step, index=None, data=None):

        d_index = {
            Heure.l_fields()[Heure.l_groupindex[0]].name: Heure.l_fields()[Heure.l_groupindex[0]].type(index)
        }

        form_man = FormLoader([], [Heure.sequence_field()], use_groupindex=True)

        if step % Heure.nb_step_form == 0:
            index_node = StringFields(
                title='Semaine', name='index', missing=-1, l_choices=zip(Heure.list('week'), Heure.list('week'))
            )
            form_man.load_init_form(Heure.action_field, index_node)

        else:
            l_names = [f.name for f in Heure.l_fields() + Heure.l_index]
            data_db = {
                Heure.sequence_field().name:
                    [{k: v for k, v in h.__dict__.items() if k in l_names} for h in Heure.from_groupindex_(d_index)]
            }
            mapping_fields = ['heure']

            form_man.load(
                step % Heure.nb_step_form, data_db=data_db, data_form=data, sequence_mapping_fields=mapping_fields
            )

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):

        # Load database
        df = Heure.load_db()
        table_man = TableLoader(Heure.l_index, Heure.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Heure.l_index, Heure.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs
