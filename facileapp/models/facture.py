#!/usr/bin/python
# -*- coding: latin-1 -*-


# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields, IntegerFields, MoneyFields, DateFields, FloatFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire


class Facture(BaseModel):

    table_name = 'facture'
    l_index = [StringFields(title=u'Numéro de Facture', name='facture_id', widget=HiddenWidget(), table_reduce=True,
                            rank=0, primary_key=True)]
    l_actions = map(lambda x: (x.format(u'une facture'), x.format(u'une facture')), BaseModel.l_actions)
    action_field = StringFields(title=u'Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False, restricted=True):
        if widget:
            l_fields = \
                [StringFields(title=u"Numéro d'affaire", name='affaire_id', l_choices=Facture.list('affaire'),
                              table_reduce=True, rank=1, required=True),
                 StringFields(title=u'Type', name='type', l_choices=Facture.list('type'), table_reduce=True,
                              required=True),
                 StringFields(title=u'Objet', name='objet'),
                 MoneyFields(title=u'Montant facture HT', name='montant_ht', required=True),
                 FloatFields(title=u'Taux TVA', name='taux_tva', l_choices=Facture.list('tva'), required=True),
                 MoneyFields(title=u'Montant TVA', name='montant_tva', widget=HiddenWidget()),
                 MoneyFields(title=u'Montant TTC', name='montant_ttc', widget=HiddenWidget(), table_reduce=True, rank=3),
                 IntegerFields(title=u'Numéro de situation', name='situation', l_choices=Facture.list('situation'),
                               required=True),
                 DateFields(title=u'Visa', name='date_visa', missing='1970-01-01'),
                 DateFields(title=u'Encaissement', name='date_payed', missing='1970-01-01')
                 ]

            if restricted:
                l_fields[-2] = DateFields(title=u'Visa', name='date_visa', missing='1970-01-01', widget=HiddenWidget(),
                                          processing_form=lambda x: pd.Timestamp(x))
                l_fields[-1] = DateFields(title=u'Encaissement', name='date_payed', missing='1970-01-01',
                                          widget=HiddenWidget(), processing_form=lambda x: pd.Timestamp(x))
        else:
            l_fields = \
                [StringFields(title=u"Numéro d'affaire", name='affaire_id', table_reduce=True, rank=1, required=True),
                 StringFields(title=u'Type', name='type', table_reduce=True, required=True),
                 StringFields(title=u'Objet', name='objet', required=True),
                 MoneyFields(title=u'Montant facture HT', name='montant_ht', required=True),
                 FloatFields(title=u'Taux TVA', name='taux_tva', required=True),
                 MoneyFields(title=u'Montant TVA', name='montant_tva'),
                 MoneyFields(title=u'Montant TTC', name='montant_ttc', table_reduce=True, rank=3),
                 IntegerFields(title=u'Numero de situation', name='situation', required=True),
                 DateFields(title=u'Visa', name='date_visa', required=True),
                 DateFields(title=u'Encaissement', name='date_payed', required=True)]

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Facture', name=Facture.table_name, dbcols=[f.dbcol() for f in Facture.l_index + Facture.l_fields()]
        )

    @staticmethod
    def list(kw):
        if kw == 'affaire':
            return zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
        elif kw == 'situation':
            return [(i, u'Situation numero {}'.format(i)) for i in range(1, 13)]
        elif kw == 'type':
            return [(u'facture', u'Facture'), (u'avoir', u'Avoir')]
        elif kw == 'tva':
            return [(0.2, u'20%'), (0.1, u'10%'), (0.055, u'5,5%'), (0.021, u'2,1%')]
        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('facture', d_index)

        return Facture(d_index, s.loc[[f.name for f in Facture.l_fields()]].to_dict())

    @staticmethod
    def load_db(**kwargs):
        l_fields = Facture.l_index + Facture.l_fields() + Facture.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='facture', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_facture():
        df_facture = Facture.load_db(columns=['facture_id'])

        if df_facture.empty:
            return []

        return df_facture['facture_id'].unique()

    @staticmethod
    def merge_affaire(l_af):

        # Get main and sub affaire
        main = '/'.join([l_af[0].affaire_num, l_af[0].affaire_ind])
        sub = '/'.join([l_af[-1].affaire_num, l_af[-1].affaire_ind])

        # Load commande and update affaire id
        df = Facture.driver.select(Facture.table_name, **{"affaire_id": sub})
        df['affaire_id'] = main

        # Save changes
        Facture.driver.update_rows(df, Facture.table_name)

    def add(self):
        l_factures = list(Facture.load_db(columns=['facture_id', 'type']).values)

        # Save current facture id
        facture_id_ = self.facture_id

        if self.facture_id == '' or self.facture_id is None:
            import IPython
            IPython.embed()
            if self.type == 'facture':
                l_factures_sub = [t[0] for t in l_factures if t[1] == 'facture']
                self.facture_id = 'FC{0:0=4d}'.format(max(map(lambda x: int(x.replace('FC', '')), l_factures_sub)) + 1)

            else:
                l_factures_sub = [t[0] for t in l_factures if t[1] == 'facture']
                self.facture_id = 'AV{0:0=4d}'.format(max(map(lambda x: int(x.replace('AV', '')), l_factures_sub)) + 1)

                if self.montant_ht > 0:
                    self.montant_ht *= -1

        # Get taxes additionnal informations
        self.montant_ttc, self.montant_tva = Facture.get_montant(
            self.__getattribute__('montant_ht'), self.__getattribute__('taux_tva')
        )

        # Try to add and reset conatct id if failed
        try:
            super(Facture, self).add()

        except ValueError, e:
            self.facture_id = facture_id_
            raise ValueError(e.message)

        return self

    def alter(self):

        self.montant_ttc, self.montant_tva = Commande.get_montant(
            self.__getattribute__('montant_ht'), self.__getattribute__('taux_tva')
        )

        super(Facture, self).alter()

        return self

    @staticmethod
    def get_montant(montant_ht, taux_tva):
        montant_tva = taux_tva * montant_ht
        return montant_tva + montant_ht, montant_tva

    @staticmethod
    def form_loading(step, index=None, data=None, restricted=True):

        if index is not None:
            d_index = {Facture.l_index[0].name: Facture.l_index[0].processing_db['upload'](index)}
        else:
            d_index = None

        form_man = FormLoader(Facture.l_index, Facture.l_fields(widget=True, restricted=restricted))

        if step % Facture.nb_step_form == 0:
            index_node = StringFields(
                title=u'Numero de facture', name='index', missing=-1,
                l_choices=zip(Facture.get_facture(), Facture.get_facture()) + [(u'new', u'Nouveau')],
                desc=u"En cas de modification choisir un numero de facture"
            )
            form_man.load_init_form(Facture.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Facture.from_index_(d_index).__dict__

            form_man.load(step % Facture.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Facture.load_db()
        table_man = TableLoader(Facture.l_index, Facture.l_fields(), limit=10, type=type)

        if type == 'excel':
            # Get processed table
            df = table_man.load_full_table(df)

            # Save excel file
            writer = pd.ExcelWriter(full_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Feuille1', index=False)
            writer.save()

            return

        if reduced:
            df, kwargs = table_man.load_reduce_table(df)
            d_footer = None

        else:
            table_man = TableLoader(Facture.l_index, Facture.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Facture.load_db()

        # Load table manager
        table_man = TableLoader(Facture.l_index, Facture.l_fields())

        # App 1 table of bill waiting for visa
        ref_date = pd.Timestamp('1970-01-01')
        df['date_visa'] = df.date_visa.apply(lambda x: pd.Timestamp(x))
        df['date_payed'] = df.date_payed.apply(lambda x: pd.Timestamp(x))

        df_, d_footer, kwargs = table_man.load_full_table(
            df.loc[df.date_visa.apply(lambda x: pd.isna(x) or x == '' or x == ref_date)]
        )

        d_control_data['tablenovisa'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'nothing'},
            'rows': [('title', [{'content': 'title', 'value': u'Factures en attente de visa', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 0
                }
        # App 2 table of bill waiting for payment
        df_, d_footer, kwargs = table_man.load_full_table(
            df.loc[~df.date_visa.apply(lambda x: pd.isna(x) or x == '' or x == ref_date) &
                   df.date_payed.apply(lambda x: pd.isna(x) or x == '' or x == ref_date)])
        d_control_data['tablenopayement'] = {
            'table': {'df': df_.copy(), 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'visa'},
            'rows': [('title', [{'content': 'title', 'value': u'Factures en attente de paiement', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 1
                }

        # App 3 table of bill payed
        df_, d_footer, kwargs = table_man.load_full_table(df.loc[df.date_payed > ref_date])
        d_control_data['tablepayment'] = {
            'table': {'df': df_, 'd_footer': d_footer, 'kwargs': kwargs, 'key': 'payement'},
            'rows': [('title', [{'content': 'title', 'value': u'Factures encaissées', 'cls': 'text-center'}]),
                     ('Table', [{'content': 'table'}])],
            'rank': 2
                }

        return d_control_data


def name_from_row(row):
    if row['is_visa'] == 'yes' and row['is_payed'] == 'no':
        return 'Mandate'

    elif row['is_visa'] == 'yes' and row['is_payed'] == 'yes':
        return 'Encaisse'

    else:
        return 'En attente de mandat'
