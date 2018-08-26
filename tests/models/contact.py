# Global imports
import unittest
import pandas as pd
import os

# Local import
from facileapp.models.contact import Contact
from facile.core.base_model import BaseModel
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class TestContact(unittest.TestCase):
    def setUp(self):
        self.d_init = {0: {'contact_id': 0, 'type': 'client', 'raison_social': 'Dassault aviation'
            , 'contact': 'Didier Deschamps', 'desc': 'sympas', 'adresse': "9 avenue Victor Hugo", 'ville': 'Clichy',
                           'code_postal': '92110', 'num_tel': '0606060606',
                           'mail': 'didier.deschamps@dassault-aviation.com', 'creation_date': str(pd.Timestamp.now()),
                           'maj_date': str(pd.Timestamp.now())},
                       1: {'contact_id': '1', 'type': 'fournisseur', 'raison_social': 'metal union',
                           'contact': 'Maurice Ravel', 'desc': 'nego facile', 'adresse': "", 'ville': 'Champigny',
                           'code_postal': '94500', 'num_tel': '0606060606', 'mail': 'maurice.ravel@metalunion.com',
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       }
        self.path = os.path.join(facile_test_path, 'contact.csv')
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

        self.d_index = {
            'contact_id': None,
        }

        self.d_data = {
            'type': 'client',
            'raison_social': 'Telehouse europe',
            'contact': 'Patrick Evra',
            'desc': 'Responsable en cas de degat materiel',
            'adresse': '100 blvd Voltaire',
            'ville': 'Paris',
            'code_postal': '75011',
            'num_tel': '0606060606',
            'mail': 'patoche@telehouse.com'
        }
        self.d_subindex = {
            'type': 'client',
            'raison_social': 'Telehouse europe',
            'contact': 'Patrick Evra',
        }

    def test_basic(self):
        """
        python -m unittest tests.models.contact.TestContact.test_basic

        """

        # Add Fournisseur
        test_contact = Contact(self.d_index, self.d_data, path=self.path)
        test_contact.add()

        # Assert new Fournisseur is in the database
        df = test_contact.load_db(self.path)
        for k, v in self.d_subindex.items():
            df = df.loc[df[k] == v]
        self.assertTrue(not df.empty)

        # Make sure same Fournisseur can't added twice
        try:
            test_contact = Contact(self.d_index, self.d_data, path=self.path)
            test_contact.add()
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

        # test alter Fournisseur
        test_contact.num_tel = '0607070707'
        test_contact.contact_id = 2
        test_contact.alter()

        # Assert record has bee changed in the database
        df = test_contact.load_db(self.path)
        df = df.loc[df['contact_id'] == 2]
        self.assertEqual(df.iloc[0]['num_tel'], '0607070707')

        # Assert deletion works
        test_contact.delete()
        df = test_contact.load_db(test_contact.path)
        for k, v in self.d_index.items():
            df = df.loc[df[k] == v]
        self.assertTrue(df.empty)

    def test_request(self):
        """
        python -m unittest tests.models.contact.TestContact.test_request
        """
        l_contact = Contact.get_contact(type_='client', path=self.path)
        self.assertEqual(len(l_contact), 1)
        self.assertEqual(l_contact[0], 'Dassault aviation - Didier Deschamps')

        l_contact = Contact.get_contact(type_='fournisseur', path=self.path)
        self.assertEqual(len(l_contact), 1)
        self.assertEqual(l_contact[0], 'metal union - Maurice Ravel')

        # Test from index instance method
        test_contact = Contact.from_index_({'contact_id': 0}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_contact.__getattribute__(k), v)

        # Test from subindex instance method
        test_contact = Contact.from_subindex_({'type': 'client', 'raison_social': 'Dassault aviation',
                                                      'contact': 'Didier Deschamps'}, path=self.path)

        for k, v in self.d_init[0].items():
            if k not in [sch.name for sch in BaseModel.l_hfields]:
                self.assertEqual(test_contact.__getattribute__(k), v)


