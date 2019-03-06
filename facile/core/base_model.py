# Global imports
import pandas as pd

# Local import
from config import d_sconfig
from facile.core.fields import StringFields
from facileapp import facile_base
from facile.utils.drivers.rdbms import RdbmsDriver


class BaseModel(object):
    table_name = ''
    l_index, l_subindex = [], []
    l_hfields = [StringFields(name='creation_date', title='creation_date', round=0),
                 StringFields(name='maj_date', title='maj_date', round=0)]
    l_actions = ['Ajouter {}', 'Modifier {}', 'Suprimer {}']
    l_documents = []
    l_apps = []
    driver = RdbmsDriver(facile_base, d_sconfig['mysql_uri'], 'BaseModel driver')

    def __init__(self, d_index, d_fields, d_hfields={}, table_name=None):
        for f in self.l_index:
            self.__setattr__(f.name, d_index[f.name])

        for f in self.l_fields():
            self.__setattr__(f.name, d_fields[f.name])

        for f in self.l_hfields:
            self.__setattr__(f.name, d_hfields.get(f.name, None))

        if table_name is not None:
            self.table_name = table_name

    @staticmethod
    def l_fields():
        raise NotImplementedError

    @staticmethod
    def declarative_base(**kwargs):
        if kwargs['name'] in facile_base.metadata.tables.keys():
            base_ = type(
                kwargs['clsname'],
                (object,),
                dict([('__tablename__', kwargs['name'])] + kwargs['dbcols'] + [f.dbcol() for f in BaseModel.l_hfields])
            )
            base_.metadata = facile_base.metadata

        else:
            base_ = type(
                kwargs['clsname'],
                (kwargs.get('base', facile_base),),
                dict([('__tablename__', kwargs['name'])] + kwargs['dbcols'] + [f.dbcol() for f in BaseModel.l_hfields])
            )

        return base_

    @staticmethod
    def list(kw):
        raise NotImplementedError

    @staticmethod
    def from_index(table_name, d_index):

        # Select element of interest
        df = BaseModel.driver.select(table_name, **d_index)

        if not df.empty:
            return df.loc[df.index[0]]
        else:
            raise IndexError('index: {} does not exist'.format(d_index))

    @staticmethod
    def from_subindex(table_name, d_subindex, l_index_names):

        # Select element of interest
        df = BaseModel.driver.select(table_name, **d_subindex)

        if not df.empty:
            return {name: df.loc[df.index[0], name] for name in l_index_names}
        else:
            raise IndexError('sub index: {} does not exist'.format(d_subindex))

    @staticmethod
    def from_groupindex(table_name, d_groupindex, l_index_names):

        # Select group of interest
        df = BaseModel.driver.select(table_name, **d_groupindex)

        if not df.empty:
            return [{name: r[name] for name in l_index_names} for _, r in df.iterrows()]
        else:
            return []

    @staticmethod
    def load_db(**kwargs):

        table_name, l_fields, columns = kwargs['table_name'], kwargs['l_fields'], kwargs['columns']
        df = BaseModel.driver.read_table(table_name, columns=columns)

        if columns is None:
            columns = df.columns

        # Load db as df
        df = df.astype({f.name: f.type for f in l_fields if f.name in columns}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields if f.name in columns})

        return df

    def add(self):
        # Update creation and maj timestamp
        self.creation_date = str(pd.Timestamp.now())
        self.maj_date = str(pd.Timestamp.now())

        # Add record and save dataframe as csv
        data = [f.type(self.__getattribute__(f.name)) for f in self.l_index + self.l_fields() + self.l_hfields]
        df_ = pd.DataFrame([data], columns=[f.name for f in self.l_index + self.l_fields() + self.l_hfields])

        # Insert value
        try:
            self.driver.insert(df_, self.table_name)
        except IndexError:
            raise IndexError('Primary key already exists')

        return self

    def alter(self):
        # Update maj timestamp
        self.maj_date = str(pd.Timestamp.now())

        # Get new values
        l_fields = self.l_index + self.l_fields() + self.l_hfields
        d_value = {f.name: f.type(self.__getattribute__(f.name)) for f in l_fields}
        d_value.pop('creation_date')
        # Update value
        self.driver.update_row(d_value, self.table_name)

        return self

    def delete(self):

        # Get new values
        l_fields = self.l_index + self.l_fields() + self.l_hfields
        d_value = {f.name: f.type(self.__getattribute__(f.name)) for f in l_fields}

        # Update value
        self.driver.delete_row(d_value, self.table_name)

        return self

    @staticmethod
    def control_loading():
        d_control_data = {'noapp': {'rows': [('title', [{'content': 'title',
                                                         'value': 'Aucun controle disponnible',
                                                         'cls': 'text-center'}]
                                              )],
                                    'rank': 0
                                    }
                          }

        return d_control_data
