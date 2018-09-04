# Global imort
import pandas as pd

# Local import
from facile.core.base_model import BaseModel


class TableManager(object):

    def __init__(self, l_index, l_fields, limit=None):
        self.l_index = l_index
        self.l_fields = l_fields
        self.limit = limit

    def render_reduce_table(self, df):
        # Sort database
        df = self.sort_df(df)

        # Get columns to display
        l_cols = [(f.name, f.rank) for f in self.l_index + self.l_fields if f.table_reduce]

        # Sort columns by rank
        l_cols = sorted(l_cols, key=lambda t: t[1])

        df = df.loc[:self.limit, [t[0] for t in l_cols]]

        return df,  {'paginate': 'true', 'record_cnt': 'true'}

    def render_full_table(self, df):
        # Sort database
        df = self.sort_df(df)

        # Get columns to display and corresponding sizes
        l_cols = [f.name for f in self.l_index + self.l_fields]

        # build footer
        d_footer = {}
        for col, s in df.iteritems():
            d_footer[col] = '_' * (2 + s.apply(lambda x: len(str(x))).max())

        return df[l_cols], d_footer, {'paginate': 'true', 'sort': 'true', 'search': 'true', 'record_cnt': 'true',
                                      'per_page': 'true', 'has_footer': True, 'responsive': True}

    @staticmethod
    def sort_df(df):
        # Sort dataframe by date of maj or creation
        df['sort_key'] = df[[f.name for f in BaseModel.l_hfields]]\
            .apply(lambda row: max([pd.Timestamp(row[f.name]) for f in BaseModel.l_hfields if row[f.name] != 'None']),
                   axis=1)
        df = df.sort_values(by='sort_key', ascending=False).reset_index(drop=True)

        return df

