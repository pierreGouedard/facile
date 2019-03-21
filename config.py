DEBUG = True
SECRET_KEY = 'changethismotherfuckingsecretkey'
MODEL_PATH = 'facileapp.models'
LST_MODEL = [
    ('user', 'User'), ('affaire', 'Affaire'), ('chantier', 'Chantier'), ('client', 'Client'), ('commande', 'Commande'),
    ('contact', 'Contact'), ('devis', 'Devis'), ('employe', 'Employe'), ('facture', 'Facture'),
    ('fournisseur', 'Fournisseur'), ('heure', 'Heure')
]

import os
FACILE_HOME = os.path.dirname(os.path.realpath(__file__))
DEFORM_TEMPLATE_PATH = os.path.join(FACILE_HOME, 'facileapp/static/deform/templates/')
TABLE_TEMPLATE_PATH = os.path.join(FACILE_HOME, 'facileapp/static/table/templates/')
FILE_DRIVER_TMP_DIR = '/tmp'

import yaml
with open('secret-config-local.yaml', 'rb') as lcf:
    d_sconfig = yaml.safe_load(lcf)
