# Global imports
import os
import pandas as pd

# Local import
import settings


class Users(object):

    id_spec = {'name': 'id', 'type': int, 'index': True}
    username_spec = {'name': 'username', 'type': str}
    password_spec = {'name': 'password', 'type': str}
    rights_spec = {'name': 'rights', 'type': str}

    path = os.path.join(settings.facile_admin_path, 'users.csv')

    def __init__(self, id, username, password, rights=None):
        self.id = id
        self.username = username
        self.password = password
        self.rights = rights

    @staticmethod
    def from_id(self, id_):
        df = self.load_users()
        if id_ in df.index:
            return Users(id_, df.loc[id_, 'username'], df.loc[id_, 'password'], df.loc[id_, 'rights'])
        else:
            raise ValueError('Id {} does not exists'.format(id_))

    @staticmethod
    def from_username(username):
        df = Users.load_users()
        s = df.loc[df.username == username].iloc[0]
        if not s.empty:
            return Users(int(s.name), s['username'], s['password'], s['rights'])
        else:
            raise ValueError('username {} does not exists'.format(username))

    @staticmethod
    def from_login(username, password):
        df = Users.load_users()

        if username in df.username.values:

            s = df.loc[df.username == username].iloc[0]
            if str(password) == str(s['password']):
                return Users(int(s.name), s['username'], s['password'], s['rights'])
            else:
                raise ValueError('password is not correct')
        else:
            raise ValueError('username {} does not exists'.format(username))

    @staticmethod
    def load_users():
        df = pd.read_csv(Users.path, index_col='id')
        return df

    def add_user(self):
        df = Users.load_users()
        id_ = df.index.max() + 1

        if self.username not in df.username:
            df = df.append(pd.DataFrame([[self.username, self.password, self.rights]], index=[id_], columns=df.columns))
            df.reset_index().to_csv(self.path)

        else:
            raise ValueError('username {} already exists'.format(self.username))

    def alter_user(self):
        df = Users.load_users()

        if self.id in df.index:

            # Alter user
            for c in df.columns:
                df.loc[self.id, c] = self.__getattribute__(c)

            # Save it
            df.reset_index().to_csv(self.path)

        else:
            raise ValueError('id {} does not exists'.format(self.username))
