# Global imports
import pandas as pd
from sqlalchemy import Column, String

# Local import
from facile.core.base_model import engine
from facileapp import facile_base


class User(object):

    d_base = {
        '__tablename__': 'users',
        'username': Column(String(250), primary_key=True),
        'password': Column(String(250)),
        'rights': Column(String(250))
    }

    def __init__(self, username, password, rights=None):
        self.username = username
        self.password = password
        self.rights = rights

    @staticmethod
    def declarative_base():

        if 'users' in facile_base.metadata.tables.keys():
            base_ = type(
                'User',
                (object,),
                User.d_base
            )
            base_.metatadata = facile_base.metadata

        else:
            base_ = type(
                'User',
                (facile_base,),
                User.d_base
            )

        return base_

    @staticmethod
    def from_username(username):

        # TODO: make correct request
        df = pd.read_sql(sql='users', con=engine)

        s = df.iloc[0]
        if not s.empty:
            return User(df[0, 'username'], df[0, 'password'], df[0, 'rights'])
        else:
            raise ValueError('username {} does not exists'.format(username))

    @staticmethod
    def from_login(username, password):

        # TODO: make correct request
        df = pd.read_sql(sql='users', con=engine)

        if not df.empty:
            if str(password) == str(df[0, 'password']):
                User.from_username(username)
            else:
                raise ValueError('password is not correct')
        else:
            raise ValueError('username {} does not exists'.format(username))

    def add(self):
        # Add record and save dataframe as csv
        df_ = pd.DataFrame([[self.username, self.password, self.rights]], columns=['username', 'password', 'rights'])
        df_.to_sql('users', engine)

    def alter(self):
        df_ = pd.DataFrame([[self.username, self.password, self.rights]], columns=['username', 'password', 'rights'])
        df_.to_sql('users', engine, if_exists='replace')

    @staticmethod
    def delete(self):
        raise NotImplementedError
