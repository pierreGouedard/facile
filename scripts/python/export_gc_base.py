#!/usr/bin/python
# -*- coding: utf-8 -*-


# Global import
import pandas as pd
import sqlalchemy as db
import os

# Local import
from facileapp import facile_base
from config import d_sconfig


# PATH TO EXCEL DB
pth_gc_base = '/home/erepie/Bureau/facile/base'
l_bases = ['base_client.csv', 'base_fournisseur.csv', 'base_chantier.csv']

# From base client we can build client table + contact client financial

# Mapping table client -> base_client
d_map_client = {
    'designation': ['CL_NOM'], 'raison_social': ['CL_RS1'], 'division': ['CL_DIV1'],
    'adresse': ['CL_ADR1'], 'cs_bp': ['CL_ADR2'], 'ville': ['CL_VILLE'], 'code_postal': ['CL_CODPOS'], 'num_tel': ['CL_TEL'],
    'mail': [None]
}

# Mapping table contact -> base_client
d_map_contact_c = {
    'type': ['CL_TYPE'], 'designation': ['CL_NOM'], 'contact': ['CL_AD1FAC'], 'desc': [None], 'adresse': ['CL_AD2FAC'],
    'cs_bp': ['CL_AD3FAC'], 'ville': ['CL_VILFAC'], 'code_postal': ['CL_CPFAC'], 'num_tel': ['CL_TELFAC'], 'mail': [None]
}


# From Base fournisseur we can build fournisseur table + contact with minimum info
d_map_founisseur = {
    'raison_social': 'FO_NOM', 'adresse': 'FO_ADR1', 'cs_bp': 'FO_ADR2', 'ville': 'FO_VILLE', 'code_postal': 'FO_CODPOS',
    'num_tel': 'FO_TEL', 'mail': [None]
}

d_map_contact_f = {
    'type': 'CL_TYPE', 'designation': 'FO_NOM', 'contact': 'FO_NOM_C1', 'desc': [None], 'adresse': [None],
    'cs_bp': [None], 'ville': [None], 'code_postal': [None], 'num_tel': 'FO_TEL_C1', 'mail': [None]
}

# OPERATION ON TEXT
f0 = lambda x: x.decode('utf-8')
f1 = lambda x: ' '.join(map(lambda y: y.lower().capitalize(), x.split(' ')))
f21 = lambda x: x.replace('Av', 'Avenue')
f22 = lambda x: x.replace('Bd', 'Boulevard')
f23 = lambda x: x.replace('Bld', 'Boulevard')
f3 = lambda x: x if len(x.split(' ')) > 1 else 'Mr/Mme {}'.format(x)

# Load client base
dtype = {
    'CL_NOM': str,
    'CL_RS1': str,
    'CL_DIV1': str,
    'CL_ADR1': str,
    'CL_ADR2': str,
    'CL_VILLE': str,
    'CL_CODPOS': str,
    'CL_TEL': str,
    'CL_TYPE': str,
    'CL_AD1FAC': str,
    'CL_AD2FAC': str,
    'CL_AD3FAC': str,
    'CL_VILFAC': str,
    'CL_CPFAC': str,
    'CL_TELFAC': str,
}

l_f1 = ['CL_RS1', 'CL_DIV1', 'CL_VILLE']
l_f2 = ['CL_ADR1']
df = pd.read_csv(os.path.join(pth_gc_base, l_bases[0]), dtype=dtype)
flatten = lambda ll: [item for l in ll for item in l if item is not None]

# Build client table
df_client = df[flatten(d_map_client.values())].copy()
df_client = df_client.fillna('')
df_client = df_client.transform({c: f0 for c in df_client.columns})
df_client[l_f1] = df_client.transform({c: f1 for c in l_f1})[l_f1]
df_client[l_f2] = df_client.transform({c: f21 for c in l_f2})[l_f2]
df_client[l_f2] = df_client.transform({c: f22 for c in l_f2})[l_f2]
df_client[l_f2] = df_client.transform({c: f23 for c in l_f2})[l_f2]

# Build contact client table
l_f1 = ['CL_AD1FAC', 'CL_AD2FAC', 'CL_VILFAC']
l_f2 = ['CL_AD2FAC']

df_contact_client = df[flatten(d_map_contact_c.values())].copy()
df_contact_client = df_contact_client.fillna('')
df_contact_client = df_contact_client.transform({c: f0 for c in df_contact_client.columns})
df_contact_client[l_f1] = df_contact_client.transform({c: f1 for c in l_f1})[l_f1]
df_contact_client[l_f2] = df_contact_client.transform({c: f21 for c in l_f2})[l_f2]
df_contact_client[l_f2] = df_contact_client.transform({c: f22 for c in l_f2})[l_f2]
df_contact_client[l_f2] = df_contact_client.transform({c: f23 for c in l_f2})[l_f2]

# Build Fournisseur Table


# Build contact fournisseur Table


# Build chantier table


import IPython
IPython.embed()




# INSERT IN BASE
# from facile.utils.drivers import rdbms
# driver = rdbms.RdbmsDriver(facile_base, d_sconfig['mysql_uri'])
# driver.insert(df, name)

# Create engin to access DB
engine = db.create_engine(d_sconfig['mysql_uri'])

