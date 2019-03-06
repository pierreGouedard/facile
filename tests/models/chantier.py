# Global imports
import unittest
import pandas as pd
import os

# Local import
from facileapp.models.chantier import Chantier
from facile.core.base_model import BaseModel

__maintainer__ = 'Pierre Gouedard'


class TestChantier(unittest.TestCase):
    def setUp(self):

        self.d_init = {0: {'chantier_id': 0, 'rs_client': 'Dassault aviation', 'nom': 'chantier rafale',
                           'contact_id': 0, 'adresse': "9 avenue Victor Hugo", 'responsable': 'Jean Dujardin',
                           'ville': 'Clichy', 'code_postal': '92110', 'is_active': 'yes',
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}}

        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'chantier_id': None,
        }

        self.d_data = {
            'rs_client': 'Telehouse europe',
            'nom': 'Chantier Datacenter Magny',
            'contact_id': 0,
            'adresse': "9 avenue Jean Jaures",
            'responsable': 'Jean Dujardin',
            'ville': 'Magny les hameaux',
            'code_postal': '78114',
            'is_active': 'yes'
        }
        self.d_subindex = {
            'rs_client': 'Telehouse europe',
            'nom': 'Chantier Datacenter Magny',
        }

    def test_basic(self):
        """
        python -m unittest tests.models.chantier.TestChantier.test_basic

        """
        # Add Fournisseur
        test_chantier = Chantier(self.d_index, self.d_data, path=self.path)
        test_chantier.add()

        # Assert new Fournisseur is in the database
        df = test_chantier.load_db(self.path)
        for k, v in self.d_subindex.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_chantier = Chantier(self.d_index, self.d_data, path=self.path)
            test_chantier.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_chantier.code_postal = '09999'
        test_chantier.chantier_id = 1
        test_chantier.alter()

        # Assert record has bee changed in the database
        df = test_chantier.load_db(self.path)
        df = df.loc[df['chantier_id'] == 1]
        self.assertEqual(df.iloc[0]['code_postal'], '09999')

        # Assert deletion works
        test_chantier.delete()
        df = test_chantier.load_db(test_chantier.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.chantier.TestChantier.test_request
        """
        # Test list chantier
        l_chantier = Chantier.get_chantier(path=self.path)
        self.assertEqual(len(l_chantier), 1)
        self.assertEqual(l_chantier[0], 'Dassault aviation - chantier rafale')

        # Test from index instance method
        test_chantier = Chantier.from_index_({'chantier_id': 0}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_chantier.__getattribute__(k), v)

        # Test from subindex instance method
        test_chantier = Chantier.from_subindex_({'rs_client': 'Dassault aviation', 'nom': 'chantier rafale'},
                                                       path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_chantier.__getattribute__(k), v)



