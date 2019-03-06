# Global imports
import unittest
import pandas as pd
import os
import numpy as np

# Local import
from facileapp.models.commande import Commande
from facile.core.base_model import BaseModel

__maintainer__ = 'Pierre Gouedard'


class TestCommande(unittest.TestCase):
    def setUp(self):
        self.commande_id = np.random.randint(100000, 999999)
        self.d_init = {0: {'commande_id': self.commande_id, 'affaire_id': 123456, 'rs_fournisseur': 'metal union',
                           'chantier_id': 0, 'responsable': 'Jean Dujardin', 'montant_ht': 15000,
                           'taux_tva': 0.196, 'montant_ttc': 17940.0, 'montant_tva': 2940.0, 'nb_article': 5,
                           'l_article': '', 'is_mandated': 'non', 'is_payed': 'non',
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'commande_id': None,
        }

        self.d_data = {
            'affaire_id': 123456,
            'rs_fournisseur': 'metal union',
            'chantier_id': 0,
            'responsable': 'Jean Dujardin',
            'montant_ht': 15000,
            'taux_tva': 0.196,
            'montant_ttc': 17940.0,
            'montant_tva': 2940.0,
            'nb_article': 10,
            'l_article': '',
            'is_mandated': 'non',
            'is_payed': 'non',
        }

    def test_basic(self):
        """
        python -m unittest tests.models.commande.TestCommande.test_basic

        """
        # Add Fournisseur
        test_commande = Commande(self.d_index, self.d_data, path=self.path)
        test_commande.add()

        # Assert new Fournisseur is in the database
        df = test_commande.load_db(test_commande.path)

        for k, v in {'commande_id': self.commande_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_commande = Commande({'commande_id': self.commande_id + 1}, self.d_data, path=self.path)
            test_commande.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_commande.nb_article = 7
        test_commande.alter()

        # Assert record has bee changed in the database
        df = test_commande.load_db(test_commande.path)

        for k, v in {'commande_id': self.commande_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['nb_article'], 7)

        # Assert deletion works
        test_commande.delete()
        df = test_commande.load_db(test_commande.path)
        for k, v in {'commande_id': self.commande_id + 1}.items():
            df = df.loc[df[k] == v]

        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.commande.TestCommande.test_request

        """
        l_commande = Commande.get_commande(path=self.path)
        self.assertEqual(len(l_commande), 1)
        self.assertEqual(l_commande[0], self.commande_id)

        # Test from index instance method
        test_commande = Commande.from_index_({'commande_id': self.commande_id}, path=self.path)
        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_commande.__getattribute__(k), v)
