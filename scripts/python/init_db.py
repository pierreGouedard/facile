# Global imports
import pandas as pd
import os

# Local import
from settings import facile_db_path
from facile.core.base_model import BaseModel
from facileapp.models.employe import Employe
from facileapp.models.client import Client
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.contact import Contact
from facileapp.models.chantier import Chantier
from facileapp.models.devis import Devis
from facileapp.models.affaire import Affaire
from facileapp.models.commande import Commande
from facileapp.models.facture import Facture
from facileapp.models.heure import Heure

__maintainer__ = 'Pierre Gouedard'


class Initializer():

    def __init__(self):
        self.path = os.path.join(facile_db_path)

    def save_database(self, df,name, ):
        df.to_csv(os.path.join(self.path, name), index=None)

    def init_tables(self):

        # Employe table
        l_cols = [f.name for f in Employe.l_index + Employe.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'employe.csv')

        # Client table
        l_cols = [f.name for f in Client.l_index + Client.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'client.csv')

        # Fournisseur table
        l_cols = [f.name for f in Fournisseur.l_index + Fournisseur.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'fournisseur.csv')

        # Contact table
        l_cols = [f.name for f in Contact.l_index + Contact.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'contact.csv')

        # Chantier table
        l_cols = [f.name for f in Chantier.l_index + Chantier.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'chantier.csv')

        # Devis table
        l_cols = [f.name for f in Devis.l_index + Devis.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'devis.csv')

        # Affaire table
        l_cols = [f.name for f in Affaire.l_index + Affaire.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'affaire.csv')

        # Commande table
        l_cols = [f.name for f in Commande.l_index + Commande.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'commande.csv')

        # Facture table
        l_cols = [f.name for f in Facture.l_index + Facture.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'facture.csv')

        # Heure table
        l_cols = [f.name for f in Heure.l_index + Heure.l_fields(widget=False) + BaseModel.l_hfields]
        self.save_database(pd.DataFrame(columns=l_cols), 'heure.csv')


if __name__ == '__main__':
    init = Initializer()
    init.init_tables()

