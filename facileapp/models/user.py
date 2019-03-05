# Global imports
import pandas as pd
from sqlalchemy import Column, String

# Local import
from facileapp import facile_base
from config import SQL_DATABASE_URI as db_uri
from facile.utils.drivers.rdbms import RdbmsDriver


class User(object):

    d_base = {
        '__tablename__': 'users',
        'username': Column(String(250), primary_key=True),
        'password': Column(String(250)),
        'rights': Column(String(250))
    }

    driver = RdbmsDriver(facile_base, db_uri, 'UserDB driver')

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

        # Get entry with correct username
        df = User.driver.select('users', **{'username': username})

        s = df.iloc[0]
        if not s.empty:
            return User(df.loc[0, 'username'], df.loc[0, 'password'], df.loc[0, 'rights'])
        else:
            raise ValueError('username {} does not exists'.format(username))

    @staticmethod
    def from_login(username, password):

        # Get entry with correct username
        df = User.driver.select('users', **{'username': username})

        # Check password is ok !
        if not df.empty:
            if str(password) == str(df.loc[0, 'password']):
                return User.from_username(username)

            else:
                raise ValueError('password is not correct')
        else:
            raise ValueError('username {} does not exists'.format(username))

    def add(self):
        # Add User
        df_ = pd.DataFrame([[self.username, self.password, self.rights]], columns=['username', 'password', 'rights'])
        self.driver.insert(df_, 'users')

    def alter(self):
        # Update user
        d_value = {k: self.__getattribute__(k) for k in ['username', 'password', 'rights']}
        self.driver.update_row(d_value, 'users')

    @staticmethod
    def delete(self):
        # Delete user
        d_value = {k: self.__getattribute__(k) for k in ['username', 'password', 'rights']}
        self.driver.delete_row(d_value, 'users')
