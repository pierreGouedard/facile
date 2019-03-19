#!/usr/bin/python
# -*- coding: latin-1 -*-

# Global imports
import pandas as pd
from sqlalchemy import Column, String

# Local import
from facileapp import facile_base
from facile.core.table_loader import TableLoader
from facile.core.fields import StringFields
from config import d_sconfig
from facile.utils.drivers.rdbms import RdbmsDriver


class User(object):

    d_base = {
        '__tablename__': 'users',
        'username': Column(String(250), primary_key=True),
        'password': Column(String(250)),
        'rights': Column(String(250))
    }

    d_fields = {
        'index': [StringFields(title='Username', name='username')],
        'fields': [
            StringFields(title='Password', name='password'),
            StringFields(
                title='Droits', name='rights',
                l_choices=[('SADMIN', 'SADMIN'), ('UADMIN', 'UADMIN'), ('CADMIN', 'CADMIN'), ('STANDARD', 'STANDARD')],
                multiple=True
            )]
    }

    driver = RdbmsDriver(facile_base, d_sconfig['mysql_uri'], 'UserDB driver')

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

    def delete(self):
        # Delete user
        d_value = {k: self.__getattribute__(k) for k in ['username', 'password', 'rights']}
        self.driver.delete_row(d_value, 'users')

    @staticmethod
    def control_loading(rights):

        d_control_data = {}
        df = User.driver.read_table('users')

        if rights != 'SADMIN':
            df.loc[df.rights == 'SADMIN', 'password'] = '******'

        # App 1 Table of user
        table_man = TableLoader(User.d_fields['index'], User.d_fields['fields'])
        df_, d_footer, kwargs = table_man.load_full_table(df, sort=False)

        d_control_data['tableuser'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'nothing'},
            'rows': [('title', [{'content': 'title', 'value': 'Utilisateur de la base', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 0
                }

        # App 2: form action on user
        action = StringFields(
            title="Action", name='action',
            l_choices=[('Ajouter', 'Ajouter'), ('Suprimer', 'Suprimer'), ('Modifier', 'modifier')]
        )
        l_nodes = [action.sn] + [f.sn for f in User.d_fields['index']] + [f.sn for f in User.d_fields['fields']]
        mapping = {'action': None, 'username': None, 'password': None, 'rights': []}

        d_control_data['setusers'] = {
            'form': {'nodes': l_nodes, 'mapping': mapping},
            'rows': [('title', [{'content': 'title', 'value': "Modification des utilisateurs", 'cls': 'text-center'}]),
                     ('form', [{'content': 'form'}])],
            'rank': 1
        }

        return d_control_data

    @staticmethod
    def control_process(form_data, session):

        form_data['success'] = True

        if session['rights'] != 'SADMIN' and 'SADMIN' in form_data['rights']:
            script = 'alert("Problem ! {}");'.format(
                "Vous ne pouvez pas faire d'action pour un super utilisateur"
            )

            return script

        if form_data['action'] == 'Ajouter':
            user = User(form_data['username'], form_data['password'], form_data['password'])
            try:
                user.add()
            except IndexError:
                form_data['err_msg'] = "l'utilisateur {} existe deja en base".format(form_data['username'])
                form_data['success'] = False

        elif form_data['action'] == 'Modifier':
            user = User(form_data['username'], form_data['password'], form_data['password'])
            try:
                user.alter()
            except IndexError:
                form_data['err_msg'] = "l'utilisateur {} n'existe pas en base".format(form_data['username'])
                form_data['success'] = False

        else:
            user = User(form_data['username'], form_data['password'], form_data['password'])
            try:
                user.delete()
            except IndexError:
                form_data['err_msg'] = "l'utilisateur {} n'existe pas en base".format(form_data['username'])
                form_data['success'] = False

        # Get script
        if form_data['success']:
            script = 'alert(%s %s);' % \
                     ('"User: {}'.format(form_data['username']), ' {} avec succes"'.format(form_data['action']))

        else:
            script = 'alert("Problem ! {}");'.format(
                form_data.get('err_msg', "Presenter vous au responsable des systemes d'information")
            )

        return script


