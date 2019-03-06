# Global imports
import sqlalchemy as db

# Local import
from facileapp import facile_base
from config import d_sconfig

__maintainer__ = 'Pierre Gouedard'


class Initializer():

    def __init__(self, uri):
        self.engine = db.create_engine(uri)

    def create_database(self):
        # Remove old db an create new
        facile_base.metadata.drop_all(self.engine)
        facile_base.metadata.create_all(self.engine)


if __name__ == '__main__':
    init = Initializer(d_sconfig['mysql_uri'])
    answer = raw_input("This action will drop every table, if you are sure enter: 'yesremoveallthis'")
    if answer == 'yesremoveallthis' or answer == "'yesremoveallthis'":
        init.create_database()
    else:
        print 'cancelled'
