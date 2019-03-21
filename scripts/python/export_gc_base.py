#!/usr/bin/python
# -*- coding: latin-1 -*-


# Global import
import pandas as pd
import sqlalchemy as db

# Local import
from facileapp import facile_base
from config import d_sconfig


pth_gc_base = ''

l_bases = ['base_chantier.xlsx', 'base_client.xlsx', 'base_fournisseur.xlsx']

# From base client we can build client table + contact client financial

# Mapping table client -> base_client
d_map_client = {
    'designation': 'CL_NOM', 'raison_social': ['CL_RS1', 'CL_RS2'], 'division': ['CL_DIV1', 'CL_DIV2'],
    'adresse': 'CL_ADR1', 'cs_bp': 'CL_ADR2', 'ville': 'CL_VILLE', 'code_postal': 'CL_CODPOS', 'num_tel': 'CL_TEL',
    'mail': None
}

# Mapping table contact -> base_client
d_map_contact = {
    'type': 'CL_TYPE', 'designation': 'CL_NOM', 'contact': 'CL_AD1FAC', 'desc': None, 'adresse': 'CL_AD2FAC',
    'cs_bp': 'CL_ADR3', 'ville': 'CL_VILFAC', 'code_postal': 'CL_CPFAC', 'num_tel': 'CL_TELFAC', 'mail': None
}


# From Base fournisseur we can build fournisseur table + contact with minimum info
d_map_founisseur = {
    'raison_social': 'FO_NOM', 'adresse': 'FO_ADR1', 'cs_bp': 'FO_ADR2', 'ville': 'FO_VILLE', 'code_postal': 'FO_CODPOS',
    'num_tel': 'FO_TEL', 'mail': None
}

d_map_contact.update({
    'type': 'CL_TYPE', 'designation': 'FO_NOM', 'contact': 'FO_NOM_C1', 'desc': None, 'adresse': None,
    'cs_bp': None, 'ville': None, 'code_postal': None, 'num_tel': 'FO_TEL_C1', 'mail': None
})


f0 = lambda x: unicode.encode(x.decode('latin1'), 'latin1')
f1 = lambda x: ' '.join(map(lambda y: y.lower().capitalize(), x.split(' ')))

f21 = lambda x: x.replace('Av', 'Avenue')
f22 = lambda x: x.replace('Bd', 'Boulevard')
f23 = lambda x: x.replace('Bld', 'Boulevard')

f3 = lambda x: x if len(x.split(' ')) > 1 else 'Mr/Mme {}'.format(x)




# Create engin to access DB
engine = db.create_engine(d_sconfig['mysql_uri'])

