# Global imports
import pandas as pd
from sqlalchemy import create_engine

# Local import
from config import SQL_DATABASE_URI as db_uri
from facile.core.fields import StringFields
from facileapp import facile_base
engine = create_engine(db_uri)


class BaseModel(object):
    name = ''
    l_index, l_subindex = [], []
    l_hfields = [StringFields(name='creation_date', title='creation_date', round=0),
                 StringFields(name='maj_date', title='maj_date', round=0)]
    l_actions = ['Ajouter {}', 'Modifier {}', 'Suprimer {}']
    l_documents = []
    l_apps = []

    def __init__(self, d_index, d_fields, d_hfields={}, name=None):
        for f in self.l_index:
            self.__setattr__(f.name, d_index[f.name])

        for f in self.l_fields():
            self.__setattr__(f.name, d_fields[f.name])

        for f in self.l_hfields:
            self.__setattr__(f.name, d_hfields.get(f.name, None))

        if name is not None:
            self.name = name

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

        # TODO write the fucking sql request
        df = pd.read_sql(sql=table_name, con=engine)

        if not df.empty:
            return df.loc[df.index[0]]
        else:
            raise IndexError('index: {} does not exist'.format(d_index))

    @staticmethod
    def from_subindex(table_name, d_subindex, l_index_names):

        # TODO write the fucking sql request
        # for k, v in d_subindex.items():
        #     df = df.loc[df[k] == v]
        df = pd.read_sql(sql=table_name, con=engine)

        if not df.empty:
            return {name: df.loc[df.index[0], name] for name in l_index_names}
        else:
            raise IndexError('sub index: {} does not exist'.format(d_subindex))

    @staticmethod
    def from_groupindex(table_name, d_groupindex, l_index_names):

        # TODO write the fucking sql request
        # for k, v in d_groupindex.items():
        #     df = df.loc[df[k] == v]
        df = pd.read_sql(sql=table_name, con=engine)

        if not df.empty:
            return [{name: r[name] for name in l_index_names} for _, r in df.iterrows()]
        else:
            return []

    @staticmethod
    def load_db(**kwargs):

        table_name, l_fields, columns = kwargs['table_name'], kwargs['l_fields'], kwargs['columns']

        # Load db as df
        df = pd.read_sql_table(table_name, engine, columns=columns) \
            .astype({f.name: f.type for f in l_fields}) \
            .fillna({f.name: f.__dict__.get('missing', '') for f in l_fields})

        return df

    def add(self):
        # Update creation and maj timestamp
        self.creation_date = str(pd.Timestamp.now())
        self.maj_date = str(pd.Timestamp.now())

        # Add record and save dataframe as csv
        data = [f.type(self.__getattribute__(f.name)) for f in self.l_index + self.l_fields() + self.l_hfields]
        df_ = pd.DataFrame([data], columns=[f.name for f in self.l_index + self.l_fields() + self.l_hfields])
        df_.to_sql(self.name, engine)
        return self

    def alter(self):
        # Update maj timestamp
        self.maj_date = str(pd.Timestamp.now())

        # TODO make request that return elment of table of interest
        df = pd.read_sql(sql=self.name, con=engine)

        # Alter record and save csv
        id_ = df_.index[0]
        for f in self.l_index + self.l_fields() + self.l_hfields:
            df.loc[id_, f.name] = f.type(self.__getattribute__(f.name))

        df.to_sql(self.name, engine, if_exists='replace')

        return self

    def delete(self):
        # TODO: make request that remove element from index
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
