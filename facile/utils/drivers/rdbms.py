# Global import
import pandas as pd
from sqlalchemy import create_engine, insert, delete, update, select, String
from sqlalchemy.exc import IntegrityError

# Local import


class RdbmsDriver(object):

    def __init__(self, base, uri, desc=''):
        self.base = base
        self.desc = desc if desc else 'rdbms driver'
        self.base.metadata.bind = create_engine(uri)

    def __str__(self):
        return '{}'.format(self.desc)

    def read_table(self, table_name, columns=None):
        return pd.read_sql_table(table_name, columns=columns, con=self.base.metadata.bind)

    def insert(self, df, table_name):
        query = insert(self.base.metadata.tables[table_name], values=df.to_dict(orient='records'))
        try:
            self.base.metadata.bind.execute(query)
        except IntegrityError:
            raise IndexError

    def delete_rows(self, df, table_name):

        for _, row in df.iterrows():
            self.delete_row(row, table_name)

    def delete_row(self, row, table_name):
        l_where_clause = []
        for col in self.base.metadata.tables[table_name].primary_key.columns:
            if isinstance(col.type, String):
                l_where_clause += ["{}.{} = '{}'".format(table_name, col.name, row[col.name])]
            else:
                l_where_clause += ["{}.{} = {}".format(table_name, col.name, row[col.name])]

        query = delete(self.base.metadata.tables[table_name], whereclause=' AND '.join(l_where_clause))
        self.base.metadata.bind.execute(query)

    def update_rows(self, df, table_name):
        for value in df.to_dict(orient='records'):
            self.update_row(value, table_name)

    def update_row(self, value, table_name):
        l_where_clause = []
        for col in self.base.metadata.tables[table_name].primary_key.columns:
            if isinstance(col.type, String):
                l_where_clause += ["{}.{} = '{}'".format(table_name, col.name, value[col.name])]
            else:
                l_where_clause += ["{}.{} = {}".format(table_name, col.name, value[col.name])]

        query = update(self.base.metadata.tables[table_name], whereclause=' AND '.join(l_where_clause), values=value)

        try:
            self.base.metadata.bind.execute(query)
        except IntegrityError:
            print 'primary_key does not exist'

    def select(self, table_name, columns=None, **kwargs):
        l_where_clause = []

        if columns is None:
            columns = [c.name for c in list(self.base.metadata.tables[table_name].columns)]

        for k, v in kwargs.items():
            col = self.base.metadata.tables[table_name].columns[k]
            if isinstance(col.type, String):
                l_where_clause += ["{}.{} = '{}'".format(table_name, col.name, v)]
            else:
                l_where_clause += ["{}.{} = {}".format(table_name, col.name, v)]

        if len(l_where_clause) > 0:
            query = select(
                from_obj=self.base.metadata.tables[table_name], columns=columns, whereclause=' AND '.join(l_where_clause)
            )
        else:
            query = select(from_obj=self.base.metadata.tables[table_name], columns=columns)

        # Get result and return dataframe
        result = self.base.metadata.bind.execute(query)

        return pd.DataFrame(list(result), columns=columns)