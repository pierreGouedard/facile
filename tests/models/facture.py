# Global imports
import unittest
import pandas as pd
import os
import numpy as np

# Local import
from facileapp.models.facture import Facture
from facile.core.base_model import BaseModel
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class TestFacture(unittest.TestCase):
    def setUp(self):
        self.facture_id = np.random.randint(100000, 999999)
        self.d_init = {0: {'facture_id': self.facture_id, 'affaire_id': 123456, 'rs_client': 'Dassault aviation',
                           'responsable': 'Jean Dujardin', 'objet': 'facture num 1', 'montant_ht': 15000,
                           'taux_tva': 0.196, 'montant_ttc': 17940.0, 'montant_tva': 2940.0, 'delai_paiement': '3 mois',
                           'is_mandated': 'non', 'is_payed': 'non', 'creation_date': str(pd.Timestamp.now()),
                           'maj_date': str(pd.Timestamp.now())}
                       }
        self.path = os.path.join(facile_test_path, 'facture.csv')
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'facture_id': None,
        }

        self.d_data = {
            'affaire_id': 123456,
            'rs_client': 'Dassault aviation',
            'responsable': 'Jean Dujardin',
            'objet': 'facture num 2',
            'montant_ht': 15000,
            'taux_tva': 0.196,
            'montant_ttc': 17940.0,
            'montant_tva': 2940.0,
            'delai_paiement': '3 mois',
            'is_mandated': 'non',
            'is_payed': 'non',
        }

    def test_basic(self):
        """
        python -m unittest tests.models.facture.TestFacture.test_basic

        """
        # Add Fournisseur
        test_facture = Facture(self.d_index, self.d_data, path=self.path)
        test_facture.add()

        # Assert new Fournisseur is in the database
        df = test_facture.load_db(test_facture.path)

        for k, v in {'facture_id': self.facture_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_facture = Facture({'facture_id': self.facture_id + 1}, self.d_data, path=self.path)
            test_facture.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_facture.objet = 'ras'
        test_facture.alter()

        # Assert record has bee changed in the database
        df = test_facture.load_db(test_facture.path)

        for k, v in {'facture_id': self.facture_id + 1}.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['objet'], 'ras')

        # Assert deletion works
        test_facture.delete()
        df = test_facture.load_db(test_facture.path)
        for k, v in {'facture_id': self.facture_id + 1}.items():
            df = df.loc[df[k] == v]

        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.facture.TestFacture.test_request

        """
        l_facture = Facture.get_facture(path=self.path)
        self.assertEqual(len(l_facture), 1)
        self.assertEqual(l_facture[0], self.facture_id)

        # Test from index instance method
        test_facture = Facture.from_index_({'facture_id': self.facture_id}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_facture.__getattribute__(k), v)
