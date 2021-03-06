# Global imort
import pandas as pd

# Local import
from facile.core.base_model import BaseModel


class TableLoader(object):

    def __init__(self, l_index, l_fields, limit=None, type='html'):
        self.l_index = l_index
        self.l_fields = l_fields
        self.limit = limit
        self.type = type

    def load_reduce_table(self, df):
        if self.type == 'html':
            return self.load_reduce_table_html(df)

    def load_full_table(self, df, l_extra_cols=None, sort=True):
        if self.type == 'html':
            return self.load_full_table_html(df, l_extra_cols=l_extra_cols, sort=sort)
        else:
            return self.load_table_excel(df, l_extra_cols=l_extra_cols, sort=sort)

    def load_table_excel(self, df, l_extra_cols=None, sort=True):
        if not df.empty and sort:
            # Sort database
            df = self.sort_df(df)

        # Get columns to display and corresponding sizes
        l_cols = [f.name for f in self.l_index + self.l_fields]

        if l_extra_cols is not None:
            l_cols += l_extra_cols

        df = df[l_cols]

        return df

    def load_reduce_table_html(self, df):

        # Get columns to display
        l_cols = [(f.name, f.rank) for f in self.l_index + self.l_fields if f.table_reduce]

        # Sort columns by rank
        l_cols = sorted(l_cols, key=lambda t: t[1])

        if not df.empty:
            # Sort database and keep latest record
            df = self.sort_df(df).loc[:self.limit, :]

        df = df.loc[:, [t[0] for t in l_cols]]

        return df,  {'paginate': 'true', 'record_cnt': 'true'}

    def load_full_table_html(self, df, l_extra_cols=None, sort=True):

        if not df.empty and sort:
            # Sort database
            df = self.sort_df(df)

        # Get columns to display and corresponding sizes
        l_cols = [f.name for f in self.l_index + self.l_fields]

        if l_extra_cols is not None:
            l_cols += l_extra_cols

        df = df[l_cols]

        # build footer
        d_footer = {}
        for col, s in df.iteritems():
            if not s.empty:
                d_footer[col] = '_' * \
                                (2 + s.apply(lambda x: len(x) if isinstance(x, (str, unicode)) else len(str(x))).max())
            else:
                d_footer[col] = '_' * len(col)

        return df, d_footer, {'paginate': 'true', 'sort': 'true', 'search': 'true', 'record_cnt': 'true',
                              'per_page': 'true', 'has_footer': True, 'responsive': True}

    @staticmethod
    def sort_df(df):
        # Sort dataframe by date of maj or creation
        df['sort_key'] = df[[f.name for f in BaseModel.l_hfields]]\
            .apply(lambda row: max([pd.Timestamp(row[f.name]) for f in BaseModel.l_hfields if row[f.name] != 'None']),
                   axis=1)
        df = df.sort_values(by='sort_key', ascending=False).reset_index(drop=True)

        return df

