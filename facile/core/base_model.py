# Global imports
import pandas as pd

# Local import
from facile.core.fields import StringFields


class ClassProperty (property):
    """Subclass property to make classmethod properties possible"""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class BaseModel(object):
    path = ''
    l_index, l_subindex = [], []
    l_hfields = [StringFields(name='creation_date', title='creation_date', round=0),
                 StringFields(name='maj_date', title='maj_date', round=0)]
    l_actions = ['Ajouter {}', 'Modifier {}', 'Suprimer {}']

    def __init__(self, d_index, d_fields, d_hfields={}, path=None):
        for f in self.l_index:
            self.__setattr__(f.name, d_index[f.name])

        for f in self.l_fields():
            self.__setattr__(f.name, d_fields[f.name])

        for f in self.l_hfields:
            self.__setattr__(f.name, d_hfields.get(f.name, None))

        if path is not None:
            self.path = path

    @staticmethod
    def l_fields():
        raise NotImplementedError

    @staticmethod
    def list(kw):
        raise NotImplementedError

    @staticmethod
    def from_index(d_index, df):

        # Retrieve record from index
        for k, v in d_index.items():
            df = df.loc[df[k] == v]

        if not df.empty:
            return df.loc[df.index[0]]
        else:
            raise ValueError('index: {} does not exist'.format(d_index))

    @staticmethod
    def from_subindex(d_subindex, l_index_names, df):

        for k, v in d_subindex.items():
            df = df.loc[df[k] == v]

        if not df.empty:
            return {name: df.loc[df.index[0], name] for name in l_index_names}
        else:
            raise ValueError('sub index: {} does not exist'.format(d_subindex))

    @staticmethod
    def load_db(path=None):
        raise NotImplementedError

    def check_subindex(self, df, b_exists=True):
        df_, l_fields = df.copy(), [self.l_fields()[i] for i in self.l_subindex]
        for f in l_fields:
            df_ = df_.loc[df_[f.name] == self.__getattribute__(f.name)]

        if b_exists and df_.empty:
            raise ValueError('subindex: {} does not exists'.format([f.name for f in l_fields]))

        elif not b_exists and not df_.empty:
            raise ValueError('subindex: {} already exists'.format([f.name for f in l_fields]))

    def add(self):
        # Update creation and maj timestamp
        self.creation_date = str(pd.Timestamp.now())
        self.maj_date = str(pd.Timestamp.now())

        # Load db
        df = self.load_db(self.path)

        # Make sure that index does not already exists
        df_ = df.copy()
        for f in self.l_index:
            df_ = df_.loc[df_[f.name] == self.__getattribute__(f.name)]

        if len(self.l_subindex) > 0:
            self.check_subindex(df, b_exists=False)

        if not df_.empty:
            raise ValueError('index: {} already exists'.format([f.name for f in self.l_index]))

        else:
            # Add record and save dataframe as csv
            data = [f.type(self.__getattribute__(f.name)) for f in self.l_index + self.l_fields() + self.l_hfields]
            df_ = pd.DataFrame([data], columns=[f.name for f in self.l_index + self.l_fields() + self.l_hfields])
            df = df.append(df_, ignore_index=True)
            df.reset_index(drop=True).to_csv(self.path, index=None)

    def alter(self):
        # Update maj timestamp
        self.maj_date = str(pd.Timestamp.now())

        # Load db
        df = self.load_db(self.path)

        # Make sure index exists
        df_ = df.copy()
        for f in self.l_index:
            df_ = df_.loc[df_[f.name] == self.__getattribute__(f.name)]

        if len(self.l_subindex) > 0:
            self.check_subindex(df, b_exists=True)

        # If empty raise error
        if df_.empty:
            raise ValueError('index: {} does not exists'.format([f.name for f in self.l_index]))

        else:
            # Alter record and save csv
            id_ = df_.index[0]
            for f in self.l_index + self.l_fields() + self.l_hfields:
                df.loc[id_, f.name] = f.type(self.__getattribute__(f.name))
            df.to_csv(self.path, index=None)

    def delete(self):
        # Load db
        df = self.load_db(self.path)

        # Identify the record to delete
        s_mask = pd.Series(index=range(len(df))).fillna(True)

        for f in self.l_index:
            s_mask &= (df[f.name] == self.__getattribute__(f.name))

        # Remove record and save db
        df = df.loc[~s_mask]

        # Save it
        df.reset_index(drop=True).to_csv(self.path, index=None)
