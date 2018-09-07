# Global imports
import pandas as pd
import os
import numpy as np
import string
import random

# Local import
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class Synthesizer():

    def __init__(self):
        self.path = os.path.join(facile_test_path)

        self.n_client = 5
        self.n_fournisseur = 5
        self.n_ouvrier = 7
        self.n_chargedaff = 3
        self.n_admin = 2
        self.n_contact_client = 10
        self.n_contact_fournisseur = 15
        self.n_chantier = 5
        self.l_affaires = range(4)
        self.d_month = {1: 'Janvier {}', 2: 'Fevrier {}', 3: 'Mars {}', 4: 'Avril {}', 5: 'Mai {}', 6: 'Juin {}',
                        7: 'Juillet {}', 8: 'Aout {}', 9: 'Septembre {}', 10: 'Octobre {}', 11: 'Novembre {}',
                        12: 'Decembre {}'}

        current_monday = (pd.Timestamp.now() - pd.Timedelta(days=pd.Timestamp.now().weekday())).date()
        l_dates = pd.DatetimeIndex(start=current_monday - pd.Timedelta(days=100),
                                   end=current_monday + pd.Timedelta(days=10),
                                   freq='w')
        self.l_semaine = [str((t + pd.Timedelta(days=1)).date()) for t in l_dates]

        self.float = lambda x: float(int(x * 1000)) / 1000
        self.name = Name()
        self.adresse = Adresse()
        self.ville = Ville()
        self.tel = Tel()
        self.service = Service()

    def save_database(self, df,name, ):
        df.to_csv(os.path.join(self.path, name), index=None)

    def Build_employe_table(self):
        np.random.seed(1234)

        d_ouvrier = {
            i: {
                'prenom': 'ouvrier',
                'nom': 'num {}'.format(i),
                'securite_social': str(np.random.randint(1e6, 9e6)),
                'carte_sejoure': ''.join([random.choice(string.ascii_letters) for _ in range(10)]),
                'emploie': np.random.choice(['CDD', 'CDI', 'interim']),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key':'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'CP'}),
                'num_tel': self.tel(),
                'mail': 'ouvrier.num_{}@casoe.com'.format(i),
                'num_entre': str(np.random.randint(100, 999)),
                'qualification': np.random.choice(["electricien", "macon", "peinture"]),
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))).date()),
                'date_end': '',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_ouvrier)}

        d_chargedaff = {
            i + self.n_ouvrier: {
                'prenom': 'chargedaff',
                'nom': 'num {}'.format(i),
                'securite_social': str(np.random.randint(1e6, 9e6)),
                'carte_sejoure': '',
                'emploie': 'CDI',
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'CP'}),
                'num_tel': self.tel(),
                'mail': 'chargedaff.num_{}@casoe.com'.format(i),
                'num_entre': str(np.random.randint(100, 999)),
                'qualification': "charge affaire",
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))).date()),
                'date_end': '',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_chargedaff)}

        d_admin = {
            i + self.n_ouvrier + self.n_chargedaff: {
                'prenom': 'admin',
                'nom': 'num {}'.format(i),
                'securite_social': str(np.random.randint(1e6, 9e6)),
                'carte_sejoure': '',
                'emploie': 'CDI',
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'CP'}),
                'num_tel': self.tel(),
                'mail': 'admin.num_{}@casoe.com'.format(i),
                'num_entre': str(np.random.randint(100, 999)),
                'qualification': "administration",
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))).date()),
                'date_end': '',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())

            }
            for i in range(self.n_admin)}

        df_employe = pd.DataFrame.from_dict(
            {k: v for k, v in d_ouvrier.items() + d_chargedaff.items() + d_admin.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_employe, 'employe.csv')

    def Build_client_table(self):
        np.random.seed(1234)

        d_client = {
            i: {
                'raison_social': 'client {}'.format(i),
                'contact': self.service(**{'seed': i, 'key': 'name'}),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@client_{}.com'.format(self.service(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_client)}

        df_client = pd.DataFrame.from_dict(
            {k: v for k, v in d_client.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_client, 'client.csv')

    def Build_fournisseur_table(self):
        np.random.seed(1234)

        d_fournisseur = {
            i: {
                'raison_social': 'fournisseur {}'.format(i),
                'contact': self.service(**{'seed': i, 'key': 'name'}),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@fournisseur_{}.com'.format(self.service(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_fournisseur)}

        df_fournisseur = pd.DataFrame.from_dict(
            {k: v for k, v in d_fournisseur.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_fournisseur, 'fournisseur.csv')

    def Build_base_prix_table(self, return_df=False):
        np.random.seed(1234)

        l_dates = pd.DatetimeIndex(start=pd.Timestamp.now().date() - pd.Timedelta(days=9000),
                                   end=pd.Timestamp.now().date() + pd.Timedelta(days=9000),
                                   freq='M')
        l_names = [self.d_month[t.month].format(t.year) for t in l_dates]

        d_base_prix = {
            i: {
                'nom': n,
                'prix_heure_be': float(np.random.randint(2000, 4000)) / 100,
                'prix_heure_ch': float(np.random.randint(500, 2000)) / 100,
                'creation_date': str(pd.Timestamp.now()),
                'maj_date': str(pd.Timestamp.now())
            }
            for i, n in enumerate(l_names)}

        df_base_prix = pd.DataFrame.from_dict(
            {k: v for k, v in d_base_prix.items()}, orient='index'
        ).reset_index(drop=True)

        if return_df:
            return df_base_prix
        self.save_database(df_base_prix, 'base_prix.csv')

    def Build_contact_table(self):
        np.random.seed(1234)

        d_contact_client = {
            i: {
                'contact_id': i,
                'type': 'client',
                'raison_social': 'client {}'.format(i % self.n_client),
                'contact': self.name(**{'seed': i, 'key': 'name'}),
                'desc': 'description of client contact {}'.format(i),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@client_{}.com'.format(self.name(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_contact_client)}

        d_contact_fournisseur = {
            i + self.n_contact_client: {
                'contact_id': i + self.n_contact_client,
                'type': 'fournisseur',
                'raison_social': 'fournisseur {}'.format(i % self.n_fournisseur),
                'contact': self.name(**{'seed': i, 'key': 'name'}),
                'desc': 'description of fournisseur contact {}'.format(i),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@fournisseur_{}.com'.format(self.name(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_contact_fournisseur)}

        df_contact = pd.DataFrame.from_dict(
            {k: v for k, v in d_contact_client.items() + d_contact_fournisseur.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_contact, 'contact.csv')

    def Build_chantier_table(self):
        np.random.seed(1234)

        d_chantier = {
            i: {
                'chantier_id': i,
                'rs_client': 'client {}'.format(i),
                'nom': 'Chantier client {}'.format(i),
                'contact_id': 0,
                'adresse': self.adresse(),
                'responsable': np.random.choice(['ouvrier num_{}'.format(j) for j in range(self.n_ouvrier)]),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'is_active': 'yes',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_chantier)}

        df_chantier = pd.DataFrame.from_dict(
            {k: v for k, v in d_chantier.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_chantier, 'chantier.csv')

    def Build_devis_table(self, return_dict_affaire=False):
        np.random.seed(1234)
        # Attached to affaire devis
        d_devis = {
            i: {'devis_id': int(i),
                'rs_client': 'client {}'.format(i),
                'contact_id': i,
                'chantier_id': i,
                'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_chargedaff)]),
                'heure_be': np.random.randint(30, 100),
                'heure_ch': np.random.randint(100, 1000),
                'montant_achat': self.float(np.random.randint(10000, 100000)),
                'coef_achat': self.float(1.5 + np.random.randn()),
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 200))).date()),
                'date_end': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 95))).date()),
                'base_prix': np.random.choice(map(lambda x: x.format(2018), self.d_month.values())),
                'price': 0.,
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i, _ in enumerate(self.l_affaires)}

        # Load base prix and compute the price of the devis
        df = self.Build_base_prix_table(return_df=True)
        for k in d_devis.keys():
            df_sub = df.loc[df.nom == d_devis[k]['base_prix']].reset_index(drop=True)

            d_devis[k]['price'] += d_devis[k]['montant_achat'] * d_devis[k]['coef_achat']
            d_devis[k]['price'] += d_devis[k]['heure_be'] * df_sub.loc[0, 'prix_heure_be']
            d_devis[k]['price'] += d_devis[k]['heure_ch'] * df_sub.loc[0, 'prix_heure_ch']
            d_devis[k]['price'] = self.float(d_devis[k]['price'])

        if return_dict_affaire:
            return d_devis

        # Add un attached devis
        d_= {len(self.l_affaires): {
            'devis_id': len(self.l_affaires),
            'rs_client': 'client {}'.format(len(self.l_affaires)),
            'contact_id': len(self.l_affaires),
            'chantier_id': len(self.l_affaires),
            'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_chargedaff)]),
            'heure_be': np.random.randint(30, 100),
            'heure_ch': np.random.randint(100, 1000),
            'montant_achat': self.float(np.random.randint(10000, 100000)),
            'coef_achat': self.float(1.5 + np.random.randn()),
            'date_start': str((pd.Timestamp.now() + pd.Timedelta(days=np.random.randint(20, 30))).date()),
            'date_end': str((pd.Timestamp.now() + pd.Timedelta(days=np.random.randint(100, 150))).date()),
            'base_prix': 'Septembre 2018',
            'price': 0.,
            'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
            'maj_date': str(pd.Timestamp.now())
        }}

        for k in d_.keys():
            df_sub = df.loc[df.nom == d_[k]['base_prix']].reset_index(drop=True)
            d_[k]['price'] += d_[k]['montant_achat'] * d_[k]['coef_achat']
            d_[k]['price'] += d_[k]['heure_be'] * df_sub.loc[0, 'prix_heure_be']
            d_[k]['price'] += d_[k]['heure_ch'] * df_sub.loc[0, 'prix_heure_ch']
            d_[k]['price'] = self.float(d_[k]['price'])

        d_devis.update(d_)

        df_devis = pd.DataFrame.from_dict(
            {k: v for k, v in d_devis.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_devis, 'devis.csv')

    def Build_commande_table(self, return_df=False):
        np.random.seed(1234)

        d_commande = {
            i: {'commande_id': i,
                'affaire_id': affaire,
                'rs_fournisseur': np.random.choice(['fournisseur {}'.format(j) for j in range(self.n_fournisseur)]),
                'chantier_id': np.random.randint(0, self.n_chantier),
                'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_chargedaff)]),
                'montant_ht': self.float(float(np.random.randint(1000, 20000))),
                'taux_tva': 0.196,
                'montant_ttc': 0.,
                'montant_tva': 0.,
                'nb_article': np.random.randint(1, 10),
                'l_article': '',
                'is_mandated': 'yes',
                'is_payed': 'yes',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i, affaire in enumerate(self.l_affaires + self.l_affaires)}

        for k in d_commande.keys():
            d_commande[k]['montant_tva'] = d_commande[k]['montant_ht'] * d_commande[k]['taux_tva']
            d_commande[k]['montant_tva'] = self.float(d_commande[k]['montant_tva'])
            d_commande[k]['montant_ttc'] = d_commande[k]['montant_ht'] + d_commande[k]['montant_tva']
            d_commande[k]['montant_ttc'] = self.float(d_commande[k]['montant_ttc'])

        df_commande = pd.DataFrame.from_dict(
            {k: v for k, v in d_commande.items()}, orient='index'
        ).reset_index(drop=True)

        if return_df:
            return df_commande

        self.save_database(df_commande, 'commande.csv')

    def Build_heure_table(self, return_df=False):
        np.random.seed(1234)

        d_heure_ouvrier = {
            i: {'heure_id': i,
                'affaire_id': affaire,
                'semaine': np.random.choice(self.l_semaine),
                'employe': np.random.choice(['ouvrier num_{}'.format(j) for j in range(self.n_ouvrier)]),
                'nb_heure_be': 0.,
                'nb_heure_ch': np.random.randint(20, 35),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                'maj_date': str(pd.Timestamp.now())
                }
            for i, affaire in enumerate(self.l_affaires + self.l_affaires + self.l_affaires + self.l_affaires)}

        d_heure_chargedaff = {
            i + len(d_heure_ouvrier): {
                'heure_id': len(d_heure_ouvrier) + i,
                'affaire_id': affaire,
                'semaine': np.random.choice(self.l_semaine),
                'employe': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_chargedaff)]),
                'nb_heure_be': np.random.randint(20, 35),
                'nb_heure_ch': 0.,
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                'maj_date': str(pd.Timestamp.now())
                }
            for i, affaire in enumerate(self.l_affaires + self.l_affaires)}

        df_heures = pd.DataFrame.from_dict(
            {k: v for k, v in d_heure_chargedaff.items() + d_heure_ouvrier.items()}, orient='index'
        ).reset_index(drop=True)

        if return_df:
            return df_heures

        self.save_database(df_heures, 'heure.csv')

    def Build_facture_table(self, return_df=False):
        np.random.seed(1234)

        d_devis, d_facture = self.Build_devis_table(return_dict_affaire=True), {}

        for k in range(3):

            d_ = {
                i + (k * len(d_devis)): {
                    'facture_id': i + (k * len(d_devis)),
                    'affaire_id': self.l_affaires[i],
                    'rs_client': d['rs_client'],
                    'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_chargedaff)]),
                    'objet': 'facture num {}'.format(k),
                    'montant_ht': self.float(d['price'] / 3),
                    'taux_tva': 0.196,
                    'montant_ttc': 0.,
                    'montant_tva': 0.,
                    'delai_paiement': 3,
                    'is_mandated': 'yes',
                    'is_payed': 'yes' if k < 2 else 'no',
                    'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                    'maj_date': str(pd.Timestamp.now())
                    }
                for i, d in enumerate(d_devis.values())}

            d_facture.update(d_)

        for k in d_facture.keys():
            d_facture[k]['montant_tva'] = d_facture[k]['montant_ht'] * d_facture[k]['taux_tva']
            d_facture[k]['montant_tva'] = self.float(d_facture[k]['montant_tva'])
            d_facture[k]['montant_ttc'] = d_facture[k]['montant_ht'] + d_facture[k]['montant_tva']
            d_facture[k]['montant_ttc'] = self.float(d_facture[k]['montant_ttc'])

        df_facture = pd.DataFrame.from_dict(
            {k: v for k, v in d_facture.items()}, orient='index'
        ).reset_index(drop=True)

        if return_df:
            return df_facture

        self.save_database(df_facture, 'facture.csv')

    def Build_affaire_table(self):

        d_affaire = {i: {
                'affaire_id': affaire,
                'devis_id': i,
                'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_chargedaff)]),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                'maj_date': str(pd.Timestamp.now())
            } for i, affaire in enumerate(self.l_affaires)}

        df_affaire = pd.DataFrame.from_dict(
            {k: v for k, v in d_affaire.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_affaire, 'affaire.csv')


class Adresse:
    name_streets = ['']

    def __call__(self, *args, **kwargs):
        num = np.random.randint(1, 100)
        qual = np.random.choice(['rue', 'avenue', 'blvd'])
        nom = np.random.choice(self.name_streets)
        return '{num} {qual} {nom}'.format(num=num, qual=qual, nom=nom)


class Ville:
    ville = [('Paris 12', '75012')]

    def __call__(self, *args, **kwargs):
        np.random.seed(kwargs.get('seed', 0))
        n = np.random.randint(0, len(self.ville))

        if kwargs.get('key', 'name') == 'name':
            return self.ville[n][0]
        else:
            return self.ville[n][1]


class Tel:
    def __call__(self, *args, **kwargs):
        return '06{}'.format(''.join([str(np.random.randint(0, 10)) for _ in range(8)]))


class Service:
    service = [('depfin', 'Departement financier'), ('service-financier', 'Service financier'),
               ('service-compta', 'Service comptabilite')]

    def __call__(self, *args, **kwargs):
        np.random.seed(kwargs.get('seed', 0))
        n = np.random.randint(0, len(self.service))

        if kwargs.get('key', 'name') == 'name':
            return self.service[n][1]
        else:
            return self.service[n][0]

class Name:
    name = ('name_{}_surname_{}', 'name_{} surname_{}')

    def __call__(self, *args, **kwargs):
        np.random.seed(kwargs.get('seed', 0))
        l = random.choice(string.ascii_letters)

        if kwargs.get('key', 'name') == 'name':
            return self.name[1].format(l, l)
        else:
            return self.name[0].format(l, l)