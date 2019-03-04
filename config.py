DEBUG = True
SECRET_KEY = 'changethismotherfuckingsecretkey'
SQL_DATABASE_URI = 'sqlite:///facile-erp.db'
MODEL_PATH = 'facileapp.models'
LST_MODEL = [
    ('user', 'User'), ('affaire', 'Affaire'), ('chantier', 'Chantier'), ('client', 'Client'), ('commande', 'Commande'),
    ('contact', 'Contact'), ('devis', 'Devis'), ('employe', 'Employe'), ('facture', 'Facture'),
    ('fournisseur', 'Fournisseur'), ('heure', 'Heure')
]
