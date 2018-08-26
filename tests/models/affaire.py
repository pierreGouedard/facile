# Global imports
import unittest
import pandas as pd
import os
import numpy as np

# Local import
from facileapp.models.affaire import Affaire
from facile.core.base_model import BaseModel
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class TestAffaire(unittest.TestCase):
    def setUp(self):
        self.affaire_id = np.random.randint(100000, 999999)
        self.d_init = {0: {'affaire_id': self.affaire_id,
                           'chantier_id': 0, 'responsable': 'Jean Dujardin', 'creation_date': str(pd.Timestamp.now()),
                           'maj_date': str(pd.Timestamp.now())}
                       }
        self.path = os.path.join(facile_test_path, 'affaire.csv')
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'affaire_id': -1,
        }

        self.d_data = {
            'contact': 'Departement financier',
            'chantier_id': 0,
            'responsable': 'Jean Dujardin'
        }

    def test_basic(self):
        """
        python -m unittest tests.models.affaire.TestAffaire.test_basic

        """
        # Add Affaire
        test_affaire = Affaire(self.d_index, self.d_data, path=self.path)
        test_affaire.add()

        # Assert new Fournisseur is in the database
        df = test_affaire.load_db(test_affaire.path)
        for k, v in {'affaire_id': self.affaire_id + 1}.items():
            df = df.loc[df[k] == v]

        self.assertTrue(not df.empty)

        # Make sure same Affaire can't added twice
        try:
            test_affaire = Affaire({'affaire_id': self.affaire_id + 1}, self.d_data, path=self.path)
            test_affaire.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # Assert deletion works
        test_affaire.delete()
        df = test_affaire.load_db(test_affaire.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.affaire.TestAffaire.test_request

        """
        l_affaire = Affaire.get_affaire(path=self.path)

        self.assertEqual(len(l_affaire), 1)
        self.assertEqual(l_affaire[0], self.affaire_id)

        # Test from index instance method
        test_affaire = Affaire.from_index_({'affaire_id': self.affaire_id}, path=self.path)
        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_affaire.__getattribute__(k), v)


