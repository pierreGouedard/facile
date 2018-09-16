# Global imports
import os
import pandas as pd

# Local import
import settings
from facile.core.fields import StringFields, FloatFields
from facile.core.form_loader import FormLoader
from facile.core.base_model import BaseModel
from facile.core.table_loader import TableLoader


class Base_prix(BaseModel):

    path = os.path.join(settings.facile_project_path, 'base_prix.csv')
    l_index = [StringFields(title="Nom de la base", name='nom', table_reduce=True, rank=0)]
    action_field = StringFields(title='Action', name='action',
                                l_choices=[('Editer une base de prix', 'Editer une base de prix')], round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        l_fields = \
            [FloatFields(title='Prix heure BE', name='prix_heure_be', table_reduce=True, rank=1),
             FloatFields(title='Prix heure Ch', name='prix_heure_ch', table_reduce=True, rank=2)]

        return l_fields

    @staticmethod
    def list(kw, **kwargs):

        d_month = {1: 'Janvier {}', 2: 'Fevrier {}', 3: 'Mars {}', 4: 'Avril {}', 5: 'Mai {}', 6: 'Juin {}',
                   7: 'Juillet {}', 8: 'Aout {}', 9: 'Septembre {}', 10: 'Octobre {}', 11: 'Novembre {}',
                   12: 'Decembre {}'}

        if kw == 'base':
            l_dates = pd.DatetimeIndex(start=pd.Timestamp.now().date() - pd.Timedelta(days=kwargs.get('b', 90)),
                                       end=pd.Timestamp.now().date() + pd.Timedelta(days=kwargs.get('a', 90)),
                                       freq='M')
            return [(d_month[t.month].format(t.year), d_month[t.month].format(t.year)) for t in l_dates]

        if kw == 'base_date':
            l_dates = pd.DatetimeIndex(start=pd.Timestamp.now().date() - pd.Timedelta(days=kwargs.get('b', 90)),
                                       end=pd.Timestamp.now().date() + pd.Timedelta(days=kwargs.get('a', 90)),
                                       freq='M')
            return [(d_month[t.month].format(t.year), t) for t in l_dates]

        elif kw == 'current_base':
            t = pd.Timestamp.now().date()
            return d_month[t.month].format(t.year)

        else:
            return []

    @staticmethod
    def from_index_(d_index, path=None):
        # Load table employe
        df = Base_prix.load_db(path)

        # Series
        s = BaseModel.from_index(d_index, df)

        return Base_prix(d_index, s.loc[[f.name for f in Base_prix.l_fields()]].to_dict(), path=path)

    @staticmethod
    def load_db(path=None):
        if path is None:
            path = Base_prix.path

        l_fields = Base_prix.l_index + Base_prix.l_fields() + Base_prix.l_hfields
        return pd.read_csv(path, dtype={f.name: f.type for f in l_fields})\
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

    @staticmethod
    def get_base(path=None):
        return Base_prix.load_db(path)['nom'].unique()

    @staticmethod
    def get_price(base, path=None):
        df = Base_prix.load_db(path)

        if not base in df.nom.unique():
            base = Base_prix.list('current_base')

        return df.loc[df['nom'] == base, ['prix_heure_be', 'prix_heure_ch']].iloc[0].to_dict()

    @staticmethod
    def form_loading(step, index=None, data=None):
        if index is not None:
            d_index = {Base_prix.l_index[0].name: index}
        else:
            d_index = None

        form_man = FormLoader(Base_prix.l_index, Base_prix.l_fields(widget=True))

        if step % Base_prix.nb_step_form == 0:
            index_node = StringFields(title='Nom de la base', name='index', missing=unicode(''),
                                      l_choices=Base_prix.list('base'), desc="une base de prix a editer")
            form_man.load_init_form(Base_prix.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Base_prix.from_index_(d_index).__dict__

            form_man.load(step % Base_prix.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True):
        # Load database
        df = Base_prix.load_db()

        if reduced:
            table_man = TableLoader(Base_prix.l_index, Base_prix.l_fields(), limit=10)
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None
        else:
            table_man = TableLoader(Base_prix.l_index, Base_prix.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Base_prix.load_db()

        d_filter = dict(zip([t[0] for t in Base_prix.list('base_date', **{'b': 300, 'a': 0})], [True] * 10))
        d_transform = dict(Base_prix.list('base_date', **{'b': 300, 'a': 0}))

        df_ = df.loc[df.nom.apply(lambda x: d_filter.get(x, False)), ['nom', 'prix_heure_ch', 'prix_heure_be']]
        df_['nom'] = df_.nom.apply(lambda x: d_transform[x])

        d_control_data['repqual'] = {
            'plot': {'k': 'series', 'd': df_.set_index('nom', drop=True)},
            'rows': [('title', [{'content': 'title', 'value': 'Evolution de la base de prix', 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
                }

        return d_control_data