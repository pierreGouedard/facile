#!/usr/bin/python
# -*- coding: latin-1 -*-

# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields, IntegerFields, FloatFields, DateFields, MoneyFields
from facile.utils.drivers.files import FileDriver
from facile.core.document_generator import WordDocument
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.client import Client
from facileapp.models.contact import Contact
from facileapp.models.employe import Employe


class Devis(BaseModel):

    table_name = 'devis'

    l_index = [StringFields(title=u'Numéro de devis', name='devis_id', widget=HiddenWidget(), table_reduce=True,
                            rank=0, primary_key=True)]
    l_documents = [('devis', 'Devis')]
    l_actions = map(lambda x: (x.format(u'un devis'), x.format(u'un devis')), BaseModel.l_actions)
    action_field = StringFields(title=u'Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 3

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title=u'Désignation client', name='designation_client', l_choices=Devis.list('client'),
                              table_reduce=True, rank=1, required=True),
                 StringFields(title=u'Contact client', name='contact_id', l_choices=Devis.list('contact'), required=True),
                 StringFields(title=u'Responsable devis', name='responsable', l_choices=Devis.list('responsable'),
                              table_reduce=True, rank=2, required=True),
                 StringFields(title=u'Désignation devis', name='object', required=True),
                 IntegerFields(title=u"Heure autre", name='heure_autre', l_choices=zip(range(9000), range(9000))),
                 IntegerFields(title=u"Heure Production", name='heure_prod', l_choices=zip(range(1000), range(1000))),
                 MoneyFields(title=u"Prix heure autre", name='prix_heure_autre', required=True),
                 MoneyFields(title=u"Prix heure Production", name='prix_heure_prod', required=True),
                 MoneyFields(title=u'Montant achat', name='montant_achat', required=True),
                 FloatFields(title=u'Coefficient achat', name='coef_achat', required=True),
                 StringFields(title=u'Base de prix', name='base_prix', l_choices=Devis.list('base_prix'), required=True),
                 DateFields(title=u'Date de début', name='date_start', required=True),
                 DateFields(title=u'Date de fin', name='date_end', required=True),
                 MoneyFields(title=u'Prix', name='price', round=2, table_reduce=True, rank=3)]
        else:
            l_fields = \
                [StringFields(title=u'Désignation client', name='designation_client', table_reduce=True, rank=1),
                 StringFields(title=u'Contact client', name='contact_id'),
                 StringFields(title=u'Responsable devis', name='responsable', table_reduce=True, rank=2),
                 StringFields(title=u'Désignation devis', name='object'),
                 IntegerFields(title=u"Heure autre", name='heure_autre'),
                 IntegerFields(title=u"Heure Production", name='heure_prod'),
                 MoneyFields(title=u"Prix heure autre", name='prix_heure_autre'),
                 MoneyFields(title=u"Prix heure Production", name='prix_heure_prod'),
                 MoneyFields(title=u'Montant achat', name='montant_achat'),
                 FloatFields(title=u'Coefficient achat', name='coef_achat'),
                 StringFields(title=u'Base de prix', name='base_prix'),
                 DateFields(title=u'Date de début', name='date_start'),
                 DateFields(title=u'Date de fin', name='date_end'),
                 MoneyFields(title=u'Prix', name='price', round=2, table_reduce=True, rank=3)]

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Devis', name=Devis.table_name, dbcols=[f.dbcol() for f in Devis.l_index + Devis.l_fields()]
        )

    @staticmethod
    def list(kw):

        d_month = {
            1: 'Janvier {}', 2: 'Fevrier {}', 3: 'Mars {}', 4: 'Avril {}', 5: 'Mai {}', 6: 'Juin {}', 7: 'Juillet {}',
            8: 'Aout {}', 9: 'Septembre {}', 10: 'Octobre {}', 11: 'Novembre {}', 12: 'Decembre {}'
        }

        if kw == 'client':
            return zip(Client.get_clients(), Client.get_clients())
        elif kw == 'contact':
            return Contact.get_contact('client_commande', return_id=True)
        elif kw == 'responsable':
            return zip(Employe.get_employes(**{'categorie': 'charge affaire'}),
                       Employe.get_employes(**{'categorie': 'charge affaire'}))
        elif kw == 'base_prix':
            d = pd.Timestamp.now().date()
            l_dates = pd.DatetimeIndex(start=d - pd.Timedelta(days=95), end=d + pd.Timedelta(days=95), freq='M')
            return [(d_month[t.month].format(t.year), d_month[t.month].format(t.year)) for t in l_dates]
        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index(Devis.table_name, d_index)

        return Devis(d_index, s.loc[[f.name for f in Devis.l_fields()]].to_dict())

    @staticmethod
    def load_db(**kwargs):

        l_fields = Devis.l_index + Devis.l_fields() + Devis.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='devis', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_devis():
        df_devis = Devis.load_db(columns=['devis_id'])

        if df_devis.empty:
            return []

        return df_devis['devis_id'].unique()

    def add(self):

        l_devis = Devis.get_devis()

        # Save current contact id
        devis_id_ = self.devis_id

        if self.devis_id == '' or self.devis_id is None:
            self.devis_id = 'DV{0:0=4d}'.format(max(map(lambda x: int(x.replace('DV', '')), l_devis)) + 1)

        self.price = Devis.compute_price(
            {'hp': self.__getattribute__('heure_prod'), 'ha': self.__getattribute__('heure_autre'),
             'php': self.__getattribute__('prix_heure_prod'), 'pha':self.__getattribute__('prix_heure_autre')},
            {'ca': self.__getattribute__('coef_achat'), 'ma': self.__getattribute__('montant_achat')}
        )

        # Try to add and reset contact id if failed
        try:
            super(Devis, self).add()

        except ValueError, e:
            self.devis_id = devis_id_
            raise ValueError(e.message)

        return self

    def alter(self, compute_price=True):
        if compute_price:
            self.price = Devis.compute_price(
                {'hp': self.__getattribute__('heure_prod'), 'ha': self.__getattribute__('heure_autre'),
                 'php': self.__getattribute__('prix_heure_prod'), 'pha': self.__getattribute__('prix_heure_autre')},
                {'ca': self.__getattribute__('coef_achat'), 'ma': self.__getattribute__('montant_achat')}
            )

        super(Devis, self).alter()

    @staticmethod
    def merge(dv_main, dv_sub):

        l_dv = [dv_main, dv_sub]

        # Get hours
        ha, hp = sum([int(dv.heure_autre) for dv in l_dv]), sum([int(dv.heure_prod) for dv in l_dv])

        # Get average price for hours
        pha = sum([(float(dv.heure_autre) / ha) * float(dv.prix_heure_autre) for dv in l_dv])
        php = sum([(float(dv.heure_prod) / hp) * float(dv.prix_heure_prod) for dv in l_dv])

        # Get command
        ma = sum([float(dv.montant_achat) for dv in l_dv])

        # Get average coef command
        ca = sum([(float(dv.montant_achat) / ma) * float(dv.coef_achat) for dv in l_dv])

        # Get dates
        ds, de = l_dv[0].date_start, max(l_dv[0].date_end, l_dv[1].date_end)

        # Define lambda for decimal
        lmbd = lambda x: float(int(x * 1000)) / 1000

        p = Devis.compute_price(
            {'ha': ha, 'hp': hp, 'pha': lmbd(pha), 'php': lmbd(php)}, {'ma': lmbd(ma), 'ca': lmbd(ca)}
        )

        # Assert precision is sufficient to maintain error low
        assert (abs(sum([float(dv.price) for dv in l_dv]) - p) < 0.001 * sum([float(dv.price) for dv in l_dv]))

        d_index = {'devis_id': l_dv[0].devis_id}
        d_fields = {f.name: l_dv[0].__getattribute__(f.name) for f in l_dv[0].l_fields()}
        d_fields.update(
            {'heure_autre': ha, 'heure_prod': hp, 'prix_heure_autre': lmbd(pha), 'prix_heure_prod': lmbd(php),
             'montant_achat': lmbd(ma), 'coef_achat': lmbd(ca), 'date_start': ds, 'date_end': de, 'price': lmbd(p)}
        )

        # Update devis
        dv_merged = Devis(d_index=d_index, d_fields=d_fields)
        return dv_merged

    @staticmethod
    def compute_price(d_heures, d_achats):
        # Compute price
        price = float(d_achats['ma']) * d_achats['ca'] + float(d_heures['hp']) * d_heures['php'] + \
                float(d_heures['ha']) * d_heures['pha']
        return float(int(price * 100)) / 100

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Devis.l_index[0].name: Devis.l_index[0].processing_db['upload'](index)}
        else:
            d_index = None

        if step % Devis.nb_step_form == 2:
            # Compute price
            price = Devis.compute_price(
                {'hp': int(data.get('heure_prod', 0)), 'ha': int(data.get('heure_autre', 0)),
                 'php': float(data.get('prix_heure_prod', 0)), 'pha': float(data.get('prix_heure_autre', 0))},
                {'ca': float(data.get('coef_achat', 1)), 'ma': float(data.get('montant_achat', 0))}
            )
            data.update({'price': price})

        form_man = FormLoader(Devis.l_index, Devis.l_fields(widget=True))

        if step % Devis.nb_step_form == 0:
            index_node = StringFields(
                title=u'Numéro de devis', name='index', missing=-1,
                l_choices=zip(Devis.get_devis(), Devis.get_devis()) + [(u'new', u'Nouveau')],
                desc=u"En cas de modification choisir un numéro de devis"
            )
            form_man.load_init_form(Devis.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Devis.from_index_(d_index).__dict__

            form_man.load(step % Devis.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Devis.load_db()
        table_man = TableLoader(Devis.l_index, Devis.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Devis.l_index, Devis.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs

    @staticmethod
    def form_document_loading():

        index_node = StringFields(
            title=u'Numéro de devis', name='index', l_choices=zip(Devis.get_devis(), Devis.get_devis())
        )
        document_node = StringFields(
            title=u'Nom document', name='document', l_choices=Devis.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

    @staticmethod
    def document_(index, path, driver=FileDriver('doc_devis', ''), name='doc_devis.docx'):

        df = Devis.load_db()
        df = df.loc[df.devis_id == index[Devis.l_index[0].name]]

        # Load contact
        df_contact = Contact.load_db()

        # Load client
        df_client = Client.load_db()
        s_client = df_client.loc[df_client.designation == df['designation_client'].iloc[0]].iloc[0]
        s_contact = df_contact.loc[df_contact.contact_id == df['contact_id'].iloc[0]].iloc[0]
        word_document = WordDocument(path, driver, {})

        # Document title
        title = u'DEVIS {}'.format(index[Devis.l_index[0].name])
        word_document.add_title(title, font_size=15, text_align='center', color='000000')
        word_document.add_field(u'Désignation client', s_client['designation'], left_indent=0.15, space_before=1.)
        word_document.add_field(
            u'Contact client',
            u'{} ({})'.format(s_contact['contact_id'], s_contact['contact']),
            left_indent=0.15, space_before=0.1
        )
        word_document.add_field(u'Responsable devis', df['responsable'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Objet', df['object'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Base de prix', df['base_prix'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Date de début', df['date_start'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Date de fin', df['date_end'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Prix total', df['price'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_simple_paragraph(
            [u'Détails'], space_before=0.3, space_after=0.2, left_indent=0.15, bold=True
        )

        l_values = [[df['heure_prod'].iloc[0], df['prix_heure_prod'].iloc[0],
                     df['heure_autre'].iloc[0], df['prix_heure_autre'].iloc[0],
                     df['montant_achat'].iloc[0], df['coef_achat'].iloc[0]]]

        df_table = pd.DataFrame(
            l_values, columns=[u'Heures Prod', u'Prix Heures Prod', u'Heures Autres', u'Prix Heures Autres',
                               u'Montant achat', u'Coef achat']
        )

        word_document.add_table(df_table, index_column=-1, left_indent=0.15)

        # Save document
        word_document.save_document(name)

    @staticmethod
    def control_loading():
        d_control_data = {}
        df = Devis.load_db()

        # App 2 amount (euros) of signed devis by charge d'aff
        df_chardaff = df[['responsable', 'price']].groupby('responsable')\
            .sum()\
            .reset_index()\
            .rename(columns={'responsable': 'label', 'price': 'montant'})

        df_chardaff['hover'] = df_chardaff.montant.apply(lambda x: '{:,.2f} Euros'.format(float(int(x * 100) / 100)))

        d_control_data['devisresp'] = {
            'plot': {'k': 'bar', 'd': df_chardaff, 'o': {'val_col': 'montant', 'hover_col': 'hover'}},
            'rows': [('title', [{'content': 'title', 'value': u"Devis envoyé par chargé d'affaire", 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
        }
        return d_control_data