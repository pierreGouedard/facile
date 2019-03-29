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
l_bases = ['base_client.csv', 'base_fournisseurs.csv', 'base_chantier.csv']

# From base client we can build client table + contact client financial

# Mapping table client -> base_client
d_map_client = {
    'designation': 'CL_NOM', 'raison_social': 'CL_RS1', 'division': 'CL_DIV1',
    'adresse': 'CL_ADR1', 'cs_bp': 'CL_ADR2', 'ville': 'CL_VILLE', 'code_postal': 'CL_CODPOS', 'num_tel': 'CL_TEL',
    'mail': None
}

# Mapping table contact -> base_client
d_map_contact_c = {
    'type': 'CL_TYPE', 'designation': 'CL_NOM', 'contact': 'CL_AD1FAC', 'desc': None, 'adresse': 'CL_AD2FAC',
    'cs_bp': 'CL_AD3FAC', 'ville': 'CL_VILFAC', 'code_postal': 'CL_CPFAC', 'num_tel': 'CL_TELFAC', 'mail': None
}


# From Base fournisseur we can build fournisseur table + contact with minimum info
d_map_founisseur = {
    'raison_social': 'FO_NOM', 'adresse': 'FO_ADR1', 'cs_bp': 'FO_ADR2', 'ville': 'FO_VILLE', 'code_postal': 'FO_CODPOS',
    'num_tel': 'FO_TEL', 'mail': None
}

d_map_contact_f = {
    'type': 'FO_TYPE', 'designation': 'FO_NOM', 'contact': 'FO_NOM_C1', 'desc': None, 'adresse': 'FO_ADR1',
    'cs_bp': None, 'ville': None, 'code_postal': None, 'num_tel': 'FO_TEL_C1', 'mail': None
}

d_map_chantier = {
    'designation_client': 'CH_CLIENT', 'nom': 'CH_NOM', 'adresse': 'CH_AD1', 'ville': 'CH_VILLE',
    'code_postal': 'CH_CODPO'
}

# OPERATION ON TEXT
f0 = lambda x: x.decode('utf-8')
f1 = lambda x: ' '.join(map(lambda y: y.lower().capitalize(), x.split(' ')))
f21 = lambda x: x.replace('Av ', 'Avenue ')
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

l_f1 = ['CL_RS1', 'CL_DIV1', 'CL_VILLE', 'CL_ADR1']
l_f2 = ['CL_ADR1']
df = pd.read_csv(os.path.join(pth_gc_base, l_bases[0]), dtype=dtype)
flatten = lambda ll: [item for l in ll for item in l if item is not None]

# Build client table
df_client = df[[v for v in d_map_client.values() if v is not None]].copy()
df_client = df_client.fillna('')
df_client = df_client.transform({c: f0 for c in df_client.columns})
df_client[l_f1] = df_client.transform({c: f1 for c in l_f1})[l_f1]
df_client[l_f2] = df_client.transform({c: f21 for c in l_f2})[l_f2]
df_client[l_f2] = df_client.transform({c: f22 for c in l_f2})[l_f2]
df_client[l_f2] = df_client.transform({c: f23 for c in l_f2})[l_f2]

# Build contact client table
l_f1 = ['CL_AD1FAC', 'CL_AD2FAC', 'CL_VILFAC']
l_f2 = ['CL_AD2FAC']

df_contact_client = df[[v for v in d_map_contact_c.values() if v is not None]].copy()
df_contact_client = df_contact_client.fillna('')
df_contact_client = df_contact_client.transform({c: f0 for c in df_contact_client.columns})
df_contact_client[l_f1] = df_contact_client.transform({c: f1 for c in l_f1})[l_f1]
df_contact_client[l_f2] = df_contact_client.transform({c: f21 for c in l_f2})[l_f2]
df_contact_client[l_f2] = df_contact_client.transform({c: f22 for c in l_f2})[l_f2]
df_contact_client[l_f2] = df_contact_client.transform({c: f23 for c in l_f2})[l_f2]


# Load Fournisseur base
dtype = {
    'FO_NOM': str,
    'FO_ADR1': str,
    'FO_ADR2': str,
    'FO_VILLE': str,
    'FO_CODPOS': str,
    'FO_TEL': str,
    'FO_NOM_C1': str,
    'FO_TEL_C1': str,
}

l_f1 = ['FO_NOM', 'FO_ADR1', 'FO_VILLE']
l_f2 = ['FO_ADR1']

df = pd.read_csv(os.path.join(pth_gc_base, l_bases[1]), dtype=dtype)

# Build Fournisseur Table
df_fourniseur = df[[v for v in d_map_founisseur.values() if v is not None]].copy()
df_fourniseur = df_fourniseur.fillna('')
df_fourniseur = df_fourniseur.transform({c: f0 for c in df_fourniseur.columns})
df_fourniseur[l_f1] = df_fourniseur.transform({c: f1 for c in l_f1})[l_f1]
df_fourniseur[l_f2] = df_fourniseur.transform({c: f21 for c in l_f2})[l_f2]
df_fourniseur[l_f2] = df_fourniseur.transform({c: f22 for c in l_f2})[l_f2]
df_fourniseur[l_f2] = df_fourniseur.transform({c: f23 for c in l_f2})[l_f2]

# Build contact fournisseur Table
l_f1 = ['FO_NOM', 'FO_NOM_C1']

df_contact_fourniseur = df[[v for v in d_map_contact_f.values() if v is not None]].copy()
df_contact_fourniseur = df_contact_fourniseur.fillna('')
df_contact_fourniseur = df_contact_fourniseur.transform({c: f0 for c in df_contact_fourniseur.columns})
df_contact_fourniseur[l_f1] = df_contact_fourniseur.transform({c: f1 for c in l_f1})[l_f1]

# Load chantier Table
dtype = {
    'CH_NOM': str,
    'CH_CLIENT': str,
    'CH_ADR1': str,
    'CH_VILLE': str,
    'CH_CODPO': str,
}

df = pd.read_csv(os.path.join(pth_gc_base, l_bases[2]), dtype=dtype)

l_f1 = ['CH_NOM', 'CH_AD1', 'CH_VILLE']
l_f2 = ['CH_AD1']

# Build chantier table
df_chantier = df[[v for v in d_map_chantier.values() if v is not None]].copy()
df_chantier = df_chantier.fillna('')
df_chantier = df_chantier.transform({c: f0 for c in df_chantier.columns})
df_chantier[l_f1] = df_chantier.transform({c: f1 for c in l_f1})[l_f1]
df_chantier[l_f2] = df_chantier.transform({c: f21 for c in l_f2})[l_f2]
df_chantier[l_f2] = df_chantier.transform({c: f22 for c in l_f2})[l_f2]
df_chantier[l_f2] = df_chantier.transform({c: f23 for c in l_f2})[l_f2]


def get_new(df_old, d_map):

    df_new = pd.DataFrame(index=df_old.index, columns=[c for c, v in d_map.items() if v is None]) \
        .fillna('')

    for k, v in d_map.items():
        if v is None:
            continue
        df_new = pd.merge(df_new, pd.DataFrame(df_old[v].rename(k)), left_index=True, right_index=True)

    return df_new

# Save to csv for inspection
df_client_new = get_new(df_client, d_map_client)
df_contact_client_new = get_new(df_contact_client, d_map_contact_c)
df_fournisseur_new = get_new(df_fourniseur, d_map_founisseur)
df_contact_fournisseur_new = get_new(df_contact_fourniseur, d_map_contact_f)
df_chantier_new = get_new(df_chantier, d_map_chantier)


df_client_new.to_csv(os.path.join(pth_gc_base, 'New/client_new.csv'), encoding='utf-8')
df_contact_client_new.to_csv(os.path.join(pth_gc_base, 'New/client_contact_new.csv'), encoding='utf-8')
df_fournisseur_new.to_csv(os.path.join(pth_gc_base, 'New/fournisseur_new.csv'), encoding='utf-8')
df_contact_fournisseur_new.to_csv(os.path.join(pth_gc_base, 'New/fournisseur_contact_new.csv'), encoding='utf-8')
df_chantier_new.to_csv(os.path.join(pth_gc_base, 'New/chantier_new.csv'), encoding='utf-8')

df_client_new['creation_date'] = str(pd.Timestamp.now())
df_client_new['maj_date'] = str(pd.Timestamp.now())
df_contact_client_new['creation_date'] = str(pd.Timestamp.now())
df_contact_client_new['maj_date'] = str(pd.Timestamp.now())
df_fournisseur_new['creation_date'] = str(pd.Timestamp.now())
df_fournisseur_new['maj_date'] = str(pd.Timestamp.now())
df_contact_fournisseur_new['creation_date'] = str(pd.Timestamp.now())
df_contact_fournisseur_new['maj_date'] = str(pd.Timestamp.now())
df_chantier_new['creation_date'] = str(pd.Timestamp.now())
df_chantier_new['maj_date'] = str(pd.Timestamp.now())

d_cli = {k: True for k in df_client_new.designation.unique()}

df_contact_client_new = df_contact_client_new.loc[df_contact_client_new.contact != '']
df_contact_client_new = df_contact_client_new.loc[df_contact_client_new.designation.apply(lambda x: d_cli.get(x, False))]
df_contact_client_new = df_contact_client_new.reset_index(drop=True)
df_contact_client_new['contact_id'] = df_contact_client_new.index.map(lambda x: 'CT{0:0=4d}'.format(x + 1))

d_fou = {k: True for k in df_fournisseur_new.raison_social.unique()}
df_contact_fournisseur_new = df_contact_fournisseur_new.loc[df_contact_fournisseur_new.contact != '']
df_contact_fournisseur_new = df_contact_fournisseur_new.loc[df_contact_fournisseur_new.designation.apply(lambda x: d_fou.get(x, False))]
df_contact_fournisseur_new = df_contact_fournisseur_new.reset_index(drop=True)
df_contact_fournisseur_new['contact_id'] = df_contact_fournisseur_new.index\
    .map(lambda x: 'CT{0:0=4d}'.format(x + df_contact_client_new.index.max() + 2))

df_chantier_new['chantier_id'] = df_chantier_new.index.map(lambda x: 'CH{0:0=4d}'.format(x + 1))

# INSERT IN BASE
from facile.utils.drivers import rdbms
driver = rdbms.RdbmsDriver(facile_base, d_sconfig['mysql_uri'])
import IPython
IPython.embed()

# driver.insert(df, 'client')



