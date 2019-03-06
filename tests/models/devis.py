# Global imports
import unittest
import pandas as pd
import os
import numpy as np

# Local import
from facileapp.models.devis import Devis
from facile.core.base_model import BaseModel

__maintainer__ = 'Pierre Gouedard'


class TestDevis(unittest.TestCase):
    def setUp(self):
        self.devis_id = np.random.randint(100000, 999999)
        self.d_init = {0: {'devis_id': self.devis_id, 'rs_client': 'Dassault aviation',
                           'contact_id': 0, 'chantier_id': 0, 'responsable': 'Jean Dujardin',
                           'heure_be': np.random.randint(5, 30), 'heure_ch': np.random.randint(50, 100),
                           'montant_achat': np.random.randint(1000, 50000), 'coef_achat': 1.5 + np.random.randn(),
                           'date_start': '2018-01-01', 'date_end': '2018-03-01', 'base_prix': 'Mai 2018', 'price': 0,
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'devis_id': None,
        }

        self.d_data = {
            'rs_client': 'Dassault aviation',
            'contact_id': 0,
            'chantier_id': 0,
            'responsable': 'Jean Dujardin',
            'heure_be': np.random.randint(5, 30),
            'heure_ch': np.random.randint(50, 100),
            'montant_achat': np.random.randint(1000, 50000),
            'coef_achat': 1.5 + np.random.randn(),
            'date_start': '2018-01-01',
            'date_end': '2018-03-01',
            'base_prix': 'Mai 2018',
            'price': 0
        }

    def test_basic(self):
        """
        python -m unittest tests.models.devis.TestDevis.test_basic

        """
        # Add Fournisseur
        test_devis = Devis(self.d_index, self.d_data, path=self.path)
        test_devis.add()

        # Assert new Fournisseur is in the database
        df = test_devis.load_db(test_devis.path)

        for k, v in {'devis_id': self.devis_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_devis = Devis({'devis_id': self.devis_id + 1}, self.d_data, path=self.path)
            test_devis.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_devis.heure_ch = 9
        test_devis.alter()

        # Assert record has bee changed in the database
        df = test_devis.load_db(test_devis.path)

        for k, v in {'devis_id': self.devis_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['heure_ch'], 9)

        # Assert deletion works
        test_devis.delete()
        df = test_devis.load_db(test_devis.path)
        for k, v in {'devis_id': self.devis_id + 1}.items():
            df = df.loc[df[k] == v]

        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.devis.TestDevis.test_request

        """
        l_devis = Devis.get_devis(path=self.path)
        self.assertEqual(len(l_devis), 1)
        self.assertEqual(l_devis[0], self.devis_id)

        # Test from index instance method
        test_devis = Devis.from_index_({'devis_id': self.devis_id}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields] + ['price', 'coef_achat', 'montant_achat']:
                self.assertEqual(test_devis.__getattribute__(k), v)

            elif k in ['price', 'coef_achat', 'montant_achat']:
                self.assertAlmostEqual(test_devis.__getattribute__(k), v, delta=1e-2)


