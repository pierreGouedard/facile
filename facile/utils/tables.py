# Global import

# Local import
from facileapp.models.employe import Employe
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.chantier import Chantier
from facileapp.models.base_prix import Base_prix
from facileapp.models.affaire import Affaire
from facileapp.models.devis import Devis
from facileapp.models.facture import Facture
from facileapp.models.commande import Commande
from facileapp.models.heure import Heure

from facile.tables import html_table


def build_table_form(table_key):

    if table_key == 'employe':
        df_table = Employe.table_rendering()

    elif table_key == 'fournisseur':
        df_table = Employe.table_rendering()

    elif table_key == 'client':
        df_table = Employe.table_rendering()

    elif table_key == 'contact':
        df_table = Employe.table_rendering()

    elif table_key == 'chantier':
        df_table = Employe.table_rendering()

    elif table_key == 'base_prix':
        df_table = Employe.table_rendering()

    elif table_key == 'affaire':
        df_table = Employe.table_rendering()

    elif table_key == 'devis':
        df_table = Employe.table_rendering()

    elif table_key == 'facture':
        df_table = Employe.table_rendering()

    elif table_key == 'commande':
        df_table = Employe.table_rendering()

    elif table_key == 'heure':
        df_table = Employe.table_rendering()

    else:
        raise ValueError('key not understood {}'.format(table_key))

    table = html_table.Table(df_table.columns, 'overview-{}'.format(table_key), head_class="table-active",
                             load_jQuery=False)

    test = table.render_table_from_pandas(df_table)

    return test