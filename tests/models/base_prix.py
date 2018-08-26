# Global imports
import unittest
import pandas as pd
import os
import numpy as np
# Local import
from facileapp.models.base_prix import  Base_prix
from settings import facile_test_path

__maintainer__ = 'Pierre Gouedard'


class TestBasePrix(unittest.TestCase):
    def setUp(self):

        self.d_init = {i: {'nom': k,
                           'prix_heure_be': float(np.random.randint(1000, 2000)) / 100,
                           'prix_heure_ch': float(np.random.randint(500, 1500)) / 100,
                           'creation_date': str(pd.Timestamp.now()), 'maj_date': str(pd.Timestamp.now())}
                       for i, k in enumerate([t[0] for t in models.Base_prix.d_list['base']])}

        self.path = os.path.join(facile_test_path, 'base_prix.csv')
        pd.DataFrame.from_dict(self.d_init, orient='index').to_csv(self.path, index=None)

    def test_request(self):
        """
        python -m unittest tests.models.base_prix.TestBasePrix.test_request

        """
        l_base = Base_prix.get_base(path=self.path)
        self.assertEqual(len(l_base), len(Base_prix.d_list['base']))

        t = pd.Timestamp.now() - pd.Timedelta(days=90)
        base = Base_prix.d_month[t.month].format(t.year)
        self.assertEqual(l_base[0], base)



