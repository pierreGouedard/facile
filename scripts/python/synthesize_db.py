# Global imports
import pandas as pd
from facile.utils.drivers import rdbms


# Local import
from facileapp import facile_base
from config import d_sconfig

driver = rdbms.RdbmsDriver(facile_base, d_sconfig['mysql_uri'])

__maintainer__ = 'Pierre Gouedard'


class Synthesizer():

    def __init__(self):

        self.n_client = 5
        self.n_fournisseur = 4
        self.n_ouvrier = 7
        self.n_charge = 3
        self.n_admin = 2

        self.n_contact_client_chantier = 5
        self.n_contact_client_commandes = 5
        self.n_contact_client_admin = 5

        self.n_contact_fournisseur = 4
        self.n_chantier = 5
        self.l_affaires = ['AF19{0:0=4d}/001'.format(i) for i in range(4)]
        self.d_month = {1: 'Janvier {}', 2: 'Fevrier {}', 3: 'Mars {}', 4: 'Avril {}', 5: 'Mai {}', 6: 'Juin {}',
                        7: 'Juillet {}', 8: 'Aout {}', 9: 'Septembre {}', 10: 'Octobre {}', 11: 'Novembre {}',
                        12: 'Decembre {}'}

        current_monday = (pd.Timestamp.now() - pd.Timedelta(days=pd.Timestamp.now().weekday())).date()
        l_dates = pd.DatetimeIndex(
            start=current_monday - pd.Timedelta(days=100), end=current_monday + pd.Timedelta(days=10), freq='w'
        )
        self.l_semaine = [str((t + pd.Timedelta(days=1)).date()) for t in l_dates]
        self.float = lambda x: float(int(x * 1000)) / 1000
        self.d_contacts = {}

    def save_database(self, df, name):
        driver.insert(df, name)

    def Build_user_table(self):
        df_users = pd.DataFrame.from_dict(
            {0: {'username': 'sadmin', 'password': 'sadminpassword', 'rights': 'SADMIN'},
             1: {'username': 'fadmin', 'password': 'fadminpassword', 'rights': 'STANDARD;FADMIN'},
             2: {'username': 'cadmin', 'password': 'cadminpassword', 'rights': 'STANDARD;CADMIN'},
             3: {'username': 'standard', 'password': 'standardpassword', 'rights': 'STANDARD'}}, orient='index'
        )
        self.save_database(df_users, 'users')


if __name__ == '__main__':
    synt = Synthesizer()
    synt.Build_user_table()
