# Global import

# Local import
from facile.tables import html_table
from facileapp.models.affaire import Affaire
from facileapp.models.base_prix import Base_prix
from facileapp.models.chantier import Chantier
from facileapp.models.client import Client
from facileapp.models.commande import Commande
from facileapp.models.contact import Contact
from facileapp.models.devis import Devis
from facileapp.models.employe import Employe
from facileapp.models.facture import Facture
from facileapp.models.fournisseur import Fournisseur
from facileapp.models.heure import Heure
from facileapp.models.views.feuille_travaux import FeuilleTravaux


def build_table(table_key, reduced=True, load_jQuery=False, head_class="table-active"):

    if table_key == 'employe':
        df_table, d_footer, kwargs = Employe.table_loading(reduced=reduced)

    elif table_key == 'fournisseur':
        df_table, d_footer, kwargs = Fournisseur.table_loading(reduced=reduced)

    elif table_key == 'client':
        df_table, d_footer, kwargs = Client.table_loading(reduced=reduced)

    elif table_key == 'contact':
        df_table, d_footer, kwargs = Contact.table_loading(reduced=reduced)

    elif table_key == 'chantier':
        df_table, d_footer, kwargs = Chantier.table_loading(reduced=reduced)

    elif table_key == 'base_prix':
        df_table, d_footer, kwargs = Base_prix.table_loading(reduced=reduced)

    elif table_key == 'affaire':
        if reduced:
            df_table, d_footer, kwargs = Affaire.table_loading(reduced=reduced)
        else:
            df_table, d_footer, kwargs = FeuilleTravaux.table_loading()

    elif table_key == 'devis':
        df_table, d_footer, kwargs = Devis.table_loading(reduced=reduced)

    elif table_key == 'facture':
        df_table, d_footer, kwargs = Facture.table_loading(reduced=reduced)

    elif table_key == 'commande':
        df_table, d_footer, kwargs = Commande.table_loading(reduced=reduced)

    elif table_key == 'heure':
        df_table, d_footer, kwargs = Heure.table_loading(reduced=reduced)

    else:
        raise ValueError('key not understood {}'.format(table_key))

    table = html_table.Table(df_table.columns, 'overview-{}'.format(table_key), head_class=head_class,
                             load_jQuery=load_jQuery, **kwargs)

    html = table.render_table_from_pandas(df_table, d_footer=d_footer)

    return html