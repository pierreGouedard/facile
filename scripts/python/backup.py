# Global imports
import sqlalchemy as db
import os
import pandas as pd
# Local import
from facileapp import facile_base
from config import d_sconfig, CODEC, BACKUP_PATH, LST_MODEL
from facile.utils.drivers import rdbms

__maintainer__ = 'Pierre Gouedard'


class BackUp():

    def __init__(self, uri, path):
        self.engine = db.create_engine(uri, encoding=CODEC)
        self.key_date = '{}'.format(pd.Timestamp.now().date())
        self.path = os.path.join(path, self.key_date)

        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def backup(self, path):
        # Remove old db an create new
        driver = rdbms.RdbmsDriver(facile_base, d_sconfig['mysql_uri'])

        for table_name in LST_MODEL[1:]:
            # Get table as Dataframe
            df = driver.select(table_name[0])

            # Save Dataframe as csv
            df.to_csv(os.path.join(self.path, '{}.csv'.format(table_name[0])), index=False)


if __name__ == '__main__':
    bu = BackUp('?'.join([d_sconfig['mysql_uri'], 'charset={}'.format(CODEC.replace('-', ''))]), BACKUP_PATH)
    bu.backup(BACKUP_PATH)
