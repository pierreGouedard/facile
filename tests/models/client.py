# Global imports
import unittest
import pandas as pd
import os

# Local import
from facileapp.models.client import Client
from facile.core.base_model import BaseModel
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class TestClient(unittest.TestCase):
    def setUp(self):
        self.d_init = {0: {'raison_social': 'Dassault aviation', 'contact': 'Dept Finance Dassault Aviation',
                           'adresse': '7 blvd Claude de Bussy', 'ville': 'Saint Cloud', 'code_postal': '92210',
                           'num_tel': '0606060606', 'mail': 'finance@dassault-aviation.com', 'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        self.path = os.path.join(facile_test_path, 'client.csv')
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'raison_social': 'Telehouse Europe',
        }

        self.d_data = {
            'contact': 'Departement financier',
            'adresse': '100 blvd Voltaire',
            'ville': 'Paris',
            'code_postal': '75011',
            'num_tel': '0606060606',
            'mail': 'finance@telehouse.com'
        }

    def test_basic(self):
        """
        python -m unittest tests.models.client.TestClient.test_basic

        """
        # Add Fournisseur
        test_client = Client(self.d_index, self.d_data, path=self.path)
        test_client.add()

        # Assert new Fournisseur is in the database
        df = test_client.load_db(test_client.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_client = Client(self.d_index, self.d_data, path=self.path)
            test_client.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_client.num_tel = '0607070707'
        test_client.alter()

        # Assert record has bee changed in the database
        df = test_client.load_db(test_client.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertEqual(df.iloc[0]['num_tel'], '0607070707')

        # Assert deletion works
        test_client.delete()
        df = test_client.load_db(test_client.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.client.TestClient.test_request

        """
        l_client = Client.get_clients(path=self.path)
        self.assertEqual(len(l_client), 1)
        self.assertEqual(l_client[0], "Dassault aviation")

        # Test from index instance method
        test_client = Client.from_index_({'raison_social': 'Dassault aviation'}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_client.__getattribute__(k), v)


