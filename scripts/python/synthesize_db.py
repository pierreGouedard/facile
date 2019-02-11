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
        self.n_fournisseur = 4
        self.n_ouvrier = 7
        self.n_charge = 3
        self.n_admin = 2
        self.n_contact_client_chantier = 5
        self.n_contact_client_commandes = 5
        self.n_contact_client_admin = 5

        self.n_contact_fournisseur = 4
        self.n_chantier = 5
        self.l_affaires = ['AF19{0:0=4d}-001'.format(i) for i in range(4)]
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
        self.cs = CS()
        self.d_contacts = {}

    def save_database(self, df, name):
        df.to_csv(os.path.join(self.path, name), index=None)

    def Build_employe_table(self):
        np.random.seed(1234)

        d_ouvrier = {
            i: {
                'prenom': 'ouvrier',
                'nom': 'num {}'.format(i),
                'securite_social': str(np.random.randint(1e6, 9e6)),
                'carte_sejoure': ''.join([random.choice(string.ascii_letters) for _ in range(10)]),
                'emploie': np.random.choice(['emploie 1', 'emploie 2', 'emploie 3']),
                'categorie': 'chantier',
                'type_contrat': np.random.choice(['CDD', 'CDI', 'Stagiaire']),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'CP'}),
                'num_tel': self.tel(),
                'mail': 'ouvrier.num_{}@casoe.com'.format(i),
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))).date()),
                'date_end': '',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_ouvrier)}

        d_charge = {
            i + self.n_ouvrier: {
                'prenom': 'chargedaff',
                'nom': 'num {}'.format(i),
                'securite_social': str(np.random.randint(1e6, 9e6)),
                'carte_sejoure': '',
                'emploie': np.random.choice(['emploie 1', 'emploie 2', 'emploie 3']),
                'categorie': np.random.choice(['charge affaire', 'charge etude']),
                'type_contrat': np.random.choice(['CDD', 'CDI', 'Stagiaire']),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'CP'}),
                'num_tel': self.tel(),
                'mail': 'chargedaff.num_{}@casoe.com'.format(i),
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))).date()),
                'date_end': '',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_charge)}

        d_admin = {
            i + self.n_ouvrier + self.n_charge: {
                'prenom': 'admin',
                'nom': 'num {}'.format(i),
                'securite_social': str(np.random.randint(1e6, 9e6)),
                'carte_sejoure': '',
                'emploie': np.random.choice(['emploie 1', 'emploie 2', 'emploie 3']),
                'categorie': 'administration',
                'type_contrat': np.random.choice(['CDD', 'CDI', 'Stagiaire']),                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'CP'}),
                'num_tel': self.tel(),
                'mail': 'admin.num_{}@casoe.com'.format(i),
                'date_start': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))).date()),
                'date_end': '',
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())

            }
            for i in range(self.n_admin)}

        df_employe = pd.DataFrame.from_dict(
            {k: v for k, v in d_ouvrier.items() + d_charge.items() + d_admin.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_employe, 'employe.csv')

    def Build_client_table(self):
        np.random.seed(1234)

        d_client = {
            i: {'designation': 'client {} - site {}'.format(i, i),
                'raison_social': 'client {}'.format(i),
                'adresse': self.adresse(),
                'cs_bp': self.cs(),
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
                'adresse': self.adresse(),
                'cs_bp': self.cs(),
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

    def Build_contact_table(self):
        np.random.seed(1234)
        n = 0
        d_contact_client_chantier = {
            i + n: {
                'contact_id': 'CT{0:0=4d}'.format(i + n),
                'type': 'client_chantier',
                'designation': 'client {}'.format(i % self.n_client),
                'contact': self.name(**{'seed': i, 'key': 'name'}),
                'desc': 'Operationel sur chantier - client {}'.format(i),
                'adresse': self.adresse(),
                'cs_bp': self.cs(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@client_{}.com'.format(self.name(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_contact_client_chantier)}
        n += self.n_contact_client_chantier
        self.d_contacts.update({'chantier': [v['contact_id'] for v in d_contact_client_chantier.values()]})

        d_contact_client_commande = {
            i + n: {
                'contact_id': 'CT{0:0=4d}'.format(i + n),
                'type': 'client_commande',
                'designation': 'client {}'.format(i % self.n_client),
                'contact': self.name(**{'seed': i, 'key': 'name'}),
                'desc': 'Operationel pour commande - client {}'.format(i),
                'adresse': self.adresse(),
                'cs_bp': self.cs(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@client_{}.com'.format(self.name(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_contact_client_commandes)}
        n += self.n_contact_client_commandes
        self.d_contacts.update({'commande': [v['contact_id'] for v in d_contact_client_commande.values()]})

        d_contact_client_admin = {
            i + n: {
                'contact_id': 'CT{0:0=4d}'.format(i + n),
                'type': 'client_administration',
                'designation': 'client {}'.format(i % self.n_client),
                'contact': self.name(**{'seed': i, 'key': 'name'}),
                'desc': 'Operationel pour administration - client {}'.format(i),
                'adresse': self.adresse(),
                'cs_bp': self.cs(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@client_{}.com'.format(self.name(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_contact_client_admin)}
        n += self.n_contact_client_admin
        self.d_contacts.update({'admin': [v['contact_id'] for v in d_contact_client_admin.values()]})

        d_contact_fournisseur = {
            i + n: {
                'contact_id': 'CT{0:0=4d}'.format(i + n),
                'type': 'fournisseur',
                'designation': 'fournisseur {}'.format(i % self.n_fournisseur),
                'contact': self.name(**{'seed': i, 'key': 'name'}),
                'desc': 'description of fournisseur contact {}'.format(i),
                'adresse': self.adresse(),
                'cs_bp': self.cs(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
                'num_tel': self.tel(),
                'mail': '{}@fournisseur_{}.com'.format(self.name(**{'seed': i, 'key': 'short'}), i),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(100, 900))),
                'maj_date': str(pd.Timestamp.now())
            }
            for i in range(self.n_contact_fournisseur)}
        self.d_contacts.update({'fournisseur': [v['contact_id'] for v in d_contact_fournisseur.values()]})

        df_contact = pd.DataFrame.from_dict(
            {k: v for k, v in d_contact_client_chantier.items() + d_contact_client_commande.items() +
             d_contact_client_admin.items() + d_contact_fournisseur.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_contact, 'contact.csv')

    def Build_chantier_table(self):
        np.random.seed(1234)

        d_chantier = {
            i: {
                'chantier_id': 'CH{0:0=4d}'.format(i),
                'designation_client': 'client {}'.format(i),
                'nom': 'Chantier client {}'.format(i),
                'adresse': self.adresse(),
                'ville': self.ville(**{'seed': i, 'key': 'name'}),
                'code_postal': self.ville(**{'seed': i, 'key': 'cp'}),
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
            i: {'devis_id': 'DV{0:0=4d}'.format(int(i)),
                'designation_client': 'client {} - site {}'.format(i, i),
                'contact_id': np.random.choice([id_ for id_ in self.d_contacts.get('commande', ['unknown'])]),
                'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_charge)]),
                'object': 'Objet du devis correspond a un texte arbitraire',
                'heure_prod': np.random.randint(100, 1000),
                'heure_autre': np.random.randint(100, 1000),
                'prix_heure_prod': float(np.random.randint(40, 100)),
                'prix_heure_autre': float(np.random.randint(60, 150)),
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
        for k in d_devis.keys():
            d_devis[k]['price'] += d_devis[k]['montant_achat'] * d_devis[k]['coef_achat']
            d_devis[k]['price'] += d_devis[k]['heure_prod'] * d_devis[k]['prix_heure_prod']
            d_devis[k]['price'] += d_devis[k]['heure_autre'] * d_devis[k]['prix_heure_autre']
            d_devis[k]['price'] = self.float(d_devis[k]['price'])

        if return_dict_affaire:
            return d_devis

        # Add un attached devis
        d_ = {len(self.l_affaires): {
            'devis_id': 'DV{0:0=4d}'.format(int(len(self.l_affaires))),
            'designation_client': 'client {} - site {}'.format(len(self.l_affaires), len(self.l_affaires)),
            'contact_id': np.random.choice([id_ for id_ in self.d_contacts.get('commande', ['unknown'])]),
            'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_charge)]),
            'heure_prod': np.random.randint(100, 1000),
            'heure_autre': np.random.randint(100, 1000),
            'prix_heure_prod': float(np.random.randint(40, 100)),
            'prix_heure_autre': float(np.random.randint(60, 150)),
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
            d_[k]['price'] += d_[k]['montant_achat'] * d_[k]['coef_achat']
            d_[k]['price'] += d_[k]['heure_prod'] * d_[k]['prix_heure_prod']
            d_[k]['price'] += d_[k]['heure_autre'] * d_[k]['prix_heure_autre']
            d_[k]['price'] = self.float(d_[k]['price'])

        d_devis.update(d_)

        df_devis = pd.DataFrame.from_dict(
            {k: v for k, v in d_devis.items()}, orient='index'
        ).reset_index(drop=True)

        self.save_database(df_devis, 'devis.csv')

    def Build_commande_table(self, return_df=False):
        np.random.seed(1234)

        d_commande = {
            i: {'commande_id': 'CM{0:0=4d}'.format(i),
                'affaire_id': affaire,
                'raison_social': np.random.choice(['fournisseur {}'.format(j) for j in range(self.n_fournisseur)]),
                'montant_ht': self.float(float(np.random.randint(1000, 20000))),
                'taux_tva': 0.196,
                'montant_ttc': 0.,
                'montant_tva': 0.,
                'l_article': '',
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
                'name': np.random.choice(['ouvrier num_{}'.format(j) for j in range(self.n_ouvrier)] + ['interimaire']),
                'heure_autre': 0.,
                'heure_prod': np.random.randint(20, 35),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                'maj_date': str(pd.Timestamp.now())
                }
            for i, affaire in enumerate(self.l_affaires + self.l_affaires + self.l_affaires + self.l_affaires)}

        d_heure_chargedaff = {
            i + len(d_heure_ouvrier): {
                'heure_id': len(d_heure_ouvrier) + i,
                'affaire_id': affaire,
                'semaine': np.random.choice(self.l_semaine),
                'employe': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_charge)]),
                'heure_autre': np.random.randint(20, 35),
                'heure_prod': 0.,
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

        # Add facture
        for k in range(3):

            d_ = {
                i + (k * len(d_devis)): {
                    'type': 'facture',
                    'facture_id': 'FC{0:0=4d}'.format(i + (k * len(d_devis))),
                    'affaire_id': self.l_affaires[i],
                    'objet': 'facture num {}'.format(k),
                    'montant_ht': self.float(d['price'] / 3),
                    'situation': i + 1,
                    'date_visa': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))).date()),
                    'date_payed': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))).date()),
                    'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                    'maj_date': str(pd.Timestamp.now())
                    }
                for i, d in enumerate(d_devis.values())}

            d_facture.update(d_)

        # Add avoir
        d_ = {
            max(d_facture.keys()) + 1: {
                'type': 'avoir',
                'facture_id': 'AV{0:0=4d}'.format(1),
                'affaire_id': self.l_affaires[0],
                'objet': 'avoir situation 1',
                'montant_ht': self.float(d_devis.values()[0]['price'] / 3),
                'situation': 0,
                'date_visa': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))).date()),
                'date_payed': str((pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))).date()),
                'creation_date': str(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(5, 10))),
                'maj_date': str(pd.Timestamp.now())
            }
        }
        d_facture.update(d_)

        df_facture = pd.DataFrame.from_dict(
            {k: v for k, v in d_facture.items()}, orient='index'
        ).reset_index(drop=True)

        if return_df:
            return df_facture

        self.save_database(df_facture, 'facture.csv')

    def Build_affaire_table(self):
        d_affaire = {i: {
                'affaire_num': affaire.split('-')[0],
                'affaire_ind': affaire.split('-')[1],
                'devis_id': 'DV{0:0=4d}'.format(i),
                'responsable': np.random.choice(['chargedaff num_{}'.format(j) for j in range(self.n_charge)]),
                'chantier_id': 'CH{0:0=4d}'.format(i),
                'contact_chantier_client': self.d_contacts['chantier'][i],
                'contact_facturation_client': self.d_contacts['admin'][i],
                'contact_chantier_interne': np.random.choice(['ouvrier num_{}'.format(j) for j in range(self.n_ouvrier)]),
                'fae': 0.0,
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

class CS:
    def __call__(self, *args, **kwargs):
        return 'CS{}'.format(''.join(map(str, np.random.randint(0, 10, 5))))

class Name:
    name = ('name_{}_surname_{}', 'name_{} surname_{}')

    def __call__(self, *args, **kwargs):
        np.random.seed(kwargs.get('seed', 0))
        l = random.choice(string.ascii_letters)

        if kwargs.get('key', 'name') == 'name':
            return self.name[1].format(l, l)
        else:
            return self.name[0].format(l, l)


if __name__ == '__main__':
    synt = Synthesizer()
    synt.Build_employe_table()
    synt.Build_client_table()
    synt.Build_fournisseur_table()
    synt.Build_contact_table()
    synt.Build_chantier_table()
    synt.Build_devis_table()
    synt.Build_commande_table()
    synt.Build_heure_table()
    synt.Build_facture_table()
    synt.Build_affaire_table()

