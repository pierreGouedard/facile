# Global imports
import unittest
import pandas as pd
import os

# Local import
from facileapp.models.employe import Employe
from facile.core.base_model import BaseModel

__maintainer__ = 'Pierre Gouedard'


class TestEmploye(unittest.TestCase):
    def setUp(self):
        self.d_init = {0: {'nom': 'Dujardin', 'prenom': 'Jean', 'securite_social': '00 000 000 000 000 000',
                           'carte_sejoure': 'XXXXXXXX', 'emploie': 'charge affaire',
                           'adresse': '7 avenue du Generale de Gaule', 'ville': 'Paris', 'code_postal': '75011',
                           'num_tel': '0606060606', 'mail': 'Jean.dujardin@gmail.com', 'num_entre': '002',
                           'qualification': "gestion affaire", 'date_start': '2018-01-01', 'date_end': '',
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'nom': 'clooney',
            'prenom': 'Georges'
        }

        self.d_data = {
            'securite_social': '00 000 000 000 000 000',
            'carte_sejoure': 'XXXXXXXX',
            'emploi': 'charge affaire',
            'adresse': '7 avenue de la republique',
            'ville': 'Paris',
            'code_postal': '75012',
            'num_tel': '0606060606',
            'mail': 'georges.clooney@gmail.com',
            'num_entre': '002',
            'qualification': "gestion affaire",
            'date_start': '2018-01-01',
            'date_end': ''
        }

    def test_basic(self):
        """
        python -m unittest tests.models.employe.TestEmploye.test_basic

        """

        # Add employe
        test_employe = Employe(self.d_index, self.d_data, path=self.path)
        test_employe.add()

        # Assert new employe is in the database
        df = test_employe.load_db(test_employe.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same employe can't added twice
        try:
            test_employe = Employe(self.d_index, self.d_data, path=self.path)
            test_employe.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter employe
        test_employe.num_tel = '0607070707'
        test_employe.alter()

        # Assert record has bee changed in the database
        df = test_employe.load_db(test_employe.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['num_tel'], '0607070707')

        # Assert deletion works
        test_employe.delete()
        df = test_employe.load_db(test_employe.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.employe.TestEmploye.test_request

        """
        l_client = Employe.get_employes(path=self.path)
        self.assertEqual(len(l_client), 1)
        self.assertEqual(l_client[0], "Jean Dujardin")

        # Test from index instance method
        test_employe = Employe.from_index_({'nom': 'Dujardin', 'prenom': 'Jean'}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_employe.__getattribute__(k), v)
