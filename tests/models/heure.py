# Global imports
import unittest
import pandas as pd
import os
import numpy as np

# Local import
from facileapp.models.heure import Heure
from facile.core.base_model import BaseModel
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class TestHeure(unittest.TestCase):
    def setUp(self):
        self.heure_id = np.random.randint(100000, 999999)
        self.d_init = {0: {'heure_id': self.heure_id, 'affaire_id': 123456, 'semaine': '2018-08-30',
                           'employe': 'Jean Dujardin', 'nb_heure_be': 10, 'nb_heure_ch': 15,
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        self.path = os.path.join(facile_test_path, 'heure.csv')
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'heure_id': None,
        }

        self.d_data = {
            'affaire_id': 123456,
            'semaine': '2018-06-18',
            'employe': 'Jean Dujardin',
            'nb_heure_be': 10,
            'nb_heure_ch': 15
        }

    def test_basic(self):
        """
        python -m unittest tests.models.heure.TestHeure.test_basic

        """
        # Add Fournisseur
        test_heure = Heure(self.d_index, self.d_data, path=self.path)
        test_heure.add()

        # Assert new Fournisseur is in the database
        df = test_heure.load_db(test_heure.path)

        for k, v in {'heure_id': self.heure_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_heure = Heure({'heure_id': self.heure_id + 1}, self.d_data, path=self.path)
            test_heure.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_heure.nb_heure_ch = 30
        test_heure.alter()

        # Assert record has bee changed in the database
        df = test_heure.load_db(test_heure.path)

        for k, v in {'heure_id': self.heure_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['nb_heure_ch'], 30)

        # Assert deletion works
        test_heure.delete()
        df = test_heure.load_db(test_heure.path)
        for k, v in {'heure_id': self.heure_id + 1}.items():
            df = df.loc[df[k] == v]

        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.heure.TestHeure.test_request

        """
        l_heure = Heure.get_heure(path=self.path)
        self.assertEqual(len(l_heure), 1)
        self.assertEqual(l_heure[0], self.heure_id)

        # Test from index instance method
        test_heure = Heure.from_index_({'heure_id': self.heure_id}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_heure.__getattribute__(k), v)
