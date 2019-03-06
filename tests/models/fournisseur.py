# Global imports
import unittest
import pandas as pd
import os

# Local import
from facileapp.models.fournisseur import Fournisseur
from facile.core.base_model import BaseModel

__maintainer__ = 'Pierre Gouedard'


class TestFournisseur(unittest.TestCase):
    def setUp(self):
        self.d_init = {0: {'raison_social': 'metal union', 'contact': 'service comptabilte',
                           'adresse': '7 rue de la republique', 'ville': 'Champigny', 'code_postal': '94500',
                           'num_tel': '0606060606', 'mail': 'comptabilite@metalunion.com',
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'raison_social': 'General electric',
        }

        self.d_data = {
            'contact': 'Departement financier',
            'adresse': '7 avenue Jean Jaures',
            'ville': 'Paris',
            'code_postal': '75015',
            'num_tel': '0606060606',
            'mail': 'finance-ge@generalelectric.com'
        }

    def test_basic(self):
        """
        python -m unittest tests.models.fournisseur.TestFournisseur.test_basic

        """
        # Add Fournisseur
        test_fournisseur = Fournisseur(self.d_index, self.d_data, path=self.path)
        test_fournisseur.add()

        # Assert new Fournisseur is in the database
        df = test_fournisseur.load_db(test_fournisseur.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_fournisseur = Fournisseur(self.d_index, self.d_data, path=self.path)
            test_fournisseur.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_fournisseur.num_tel = '0607070707'
        test_fournisseur.alter()

        # Assert record has bee changed in the database
        df = test_fournisseur.load_db(test_fournisseur.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['num_tel'], '0607070707')

        # Assert deletion works
        test_fournisseur.delete()
        df = test_fournisseur.load_db(test_fournisseur.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.fournisseur.TestFournisseur.test_request

        """
        l_fournisseur = Fournisseur.get_fournisseurs(path=self.path)
        self.assertEqual(len(l_fournisseur), 1)
        self.assertEqual(l_fournisseur[0], "metal union")

        # Test from index instance method
        test_fournisseur = Fournisseur.from_index_({'raison_social': 'metal union'}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_fournisseur.__getattribute__(k), v)


