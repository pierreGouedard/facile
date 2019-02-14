# Global import

# Local import
from facile.tables import html_table
from facileapp.models.affaire import Affaire
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
from facile.utils.drivers.comon import FileDriver
from settings import facile_driver_tmpdir


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

    elif table_key == 'affaire':
        if reduced:
            df_table, d_footer, kwargs = Affaire.table_loading()
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


def process_table(table_key):

    # Clean facile doc tmpdir
    clean_tmp_dir()

    # Create tmp dir
    driver = FileDriver('tmp_doc', '')
    tmpdir = driver.TempDir(create=True, prefix='tmp_doc_')

    if table_key == 'employe':
        full_path = driver.join(tmpdir.path, 'table_employe.xlsx')
        Employe.table_loading(full_path=full_path, type='excel')

    elif table_key == 'fournisseur':
        full_path = driver.join(tmpdir.path, 'table_fournisseur.xlsx')
        Fournisseur.table_loading(full_path=full_path, type='excel')

    elif table_key == 'client':
        full_path = driver.join(tmpdir.path, 'table_client.xlsx')
        Client.table_loading(full_path=full_path, type='excel')

    elif table_key == 'contact':
        full_path = driver.join(tmpdir.path, 'table_contact.xlsx')
        Contact.table_loading(full_path=full_path, type='excel')

    elif table_key == 'chantier':
        full_path = driver.join(tmpdir.path, 'table_chantier.xlsx')
        Chantier.table_loading(full_path=full_path, type='excel')

    elif table_key == 'affaire':
        full_path = driver.join(tmpdir.path, 'table_affaire.xlsx')
        FeuilleTravaux.table_loading(full_path=full_path, type='excel')

    elif table_key == 'devis':
        full_path = driver.join(tmpdir.path, 'table_devis.xlsx')
        Devis.table_loading(full_path=full_path, type='excel')

    elif table_key == 'facture':
        full_path = driver.join(tmpdir.path, 'table_facture.xlsx')
        Facture.table_loading(full_path=full_path, type='excel')

    elif table_key == 'commande':
        full_path = driver.join(tmpdir.path, 'table_commande.xlsx')
        Commande.table_loading(full_path=full_path, type='excel')

    elif table_key == 'heure':
        full_path = driver.join(tmpdir.path, 'table_heure.xlsx')
        Heure.table_loading(full_path=full_path, type='excel')

    else:
        raise ValueError('key not understood {}'.format(table_key))
    import time
    time.sleep(1)
    return full_path, tmpdir


def clean_tmp_dir():
    driver = FileDriver('tmp_doc', '')
    for f in driver.listdir(facile_driver_tmpdir):
        if 'tmp_doc_' in f:
            try:
                driver.remove(driver.join(facile_driver_tmpdir, f), recursive=True)
            except OSError:
                continue
