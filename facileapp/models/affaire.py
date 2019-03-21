#!/usr/bin/python
# -*- coding: latin-1 -*-

# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields, MoneyFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.devis import Devis
from facileapp.models.employe import Employe
from facileapp.models.chantier import Chantier
from facileapp.models.contact import Contact


class Affaire(BaseModel):

    table_name = 'affaire'
    l_index = [StringFields(title=u"Numero d'affaire", name='affaire_num', widget=HiddenWidget(), table_reduce=True,
                            rank=0, primary_key=True),
               StringFields(title=u"Indice de l'affaire", name='affaire_ind', widget=HiddenWidget(), table_reduce=True,
                            rank=1, primary_key=True)
               ]
    l_documents = [(u'ftravaux', u'Feuille de travaux')]
    l_actions = map(lambda x: (x.format(u'une affaire'), x.format(u'une affaire')), BaseModel.l_actions) + \
        [(u'Ajouter une affaire secondaire', u'Ajouter une affaire secondaire')]

    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 3

    @staticmethod
    def l_fields(widget=False, **kwlist):
        if widget:
            l_fields = \
                [StringFields(title=u"Numéro de devis", name='devis_id', l_choices=Affaire.list('devis'),
                              table_reduce=True, rank=2, required=True),
                 StringFields(title=u'Responsable affaire', name='responsable', l_choices=Affaire.list('responsable'),
                              table_reduce=True, rank=3, required=True),
                 StringFields(title=u'Chantier', name='chantier_id', l_choices=Affaire.list('chantier', **kwlist),
                              round=2, required=True),
                 StringFields(title=u'Contact client - chantier', name='contact_chantier_client',
                              l_choices=Affaire.list('contact_chantier_client', **kwlist), round=2, required=True),
                 StringFields(title=u'Contact client - facturation', name='contact_facturation_client',
                              l_choices=Affaire.list('contact_facturation_client', **kwlist), round=2, required=True),
                 StringFields(title=u'Contact interne - chantier', name='contact_chantier_interne',
                              l_choices=Affaire.list('contact_chantier_interne', **kwlist), round=2, required=True),
                 MoneyFields(title=u'FAE', name='fae', missing=0.0, widget=HiddenWidget())]

        else:
            l_fields = \
                [StringFields(title=u"Numéro de devis", name='devis_id', table_reduce=True, rank=2, required=True),
                 StringFields(title=u'Responsable Affaire', name='responsable', table_reduce=True, rank=3, required=True),
                 StringFields(title=u'Chantier', name='chantier_id', round=2, required=True),
                 StringFields(title=u'Contact client - chantier', name='contact_chantier_client', round=2, required=True),
                 StringFields(title=u'Contact client - facturation', name='contact_facturation_client', round=2,
                              required=True),
                 StringFields(title=u'Contact interne - chantier', name='contact_chantier_interne', round=2,
                              required=True),
                 MoneyFields(title=u'FAE', name='fae', missing=0.0, widget=HiddenWidget())]

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Affaire', name=Affaire.table_name, dbcols=[f.dbcol() for f in Affaire.l_index + Affaire.l_fields()]
        )

    @staticmethod
    def list(id_, **kwlist):
        if id_ == 'responsable':
            return zip(Employe.get_employes(**{'categorie': 'charge affaire'}),
                       Employe.get_employes(**{'categorie': 'charge affaire'}))
        elif id_ == 'devis':
            return zip(Devis.get_devis(), Devis.get_devis())
        elif id_ == 'chantier':
            kwargs = kwlist.get('chantier', {})
            return Chantier.get_chantier(return_id=True, **kwargs)
        elif id_ == 'contact_chantier_client':
            return Contact.get_contact('client_chantier', return_id=True, **kwlist.get('contact', {}))
        elif id_ == 'contact_facturation_client':
            return Contact.get_contact('client_administration', return_id=True, **kwlist.get('contact', {}))
        elif id_ == 'contact_chantier_interne':
            return zip(Employe.get_employes(**{'categorie': 'chantier'}),
                       Employe.get_employes(**{'categorie': 'chantier'}))
        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index(Affaire.table_name, d_index)

        return Affaire(d_index, s.loc[[f.name for f in Affaire.l_fields()]].to_dict())

    @staticmethod
    def load_db(**kwargs):

        # Get fields
        l_fields = Affaire.l_index + Affaire.l_fields() + Affaire.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='affaire', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_affaire(sep='/'):

        # Get affaires
        df = Affaire.driver.select(Affaire.table_name, columns=['affaire_num', 'affaire_ind'])

        if df.empty:
            return []

        return df.apply(lambda r: '{}'.format(sep).join([r['affaire_num'], r['affaire_ind']]), axis=1).unique()

    def add(self):
        # Get list of affaire
        l_affaires = map(lambda x: x.split('/'), Affaire.get_affaire())

        # Save current contact id
        affaire_num_, affaire_ind_, code_year = self.affaire_num, self.affaire_ind, str(pd.Timestamp.now().year)[-2:]

        if self.affaire_num == u'' or self.affaire_num is None:
            if 'AF{}0000'.format(code_year) in [t[0] for t in l_affaires]:
                self.affaire_num = 'AF{}'.format(code_year) + '{0:0=4d}'.format(
                    max(map(lambda t: int(t[0].replace('AF{}'.format(code_year), '')), l_affaires)) + 1
                )

            else:
                self.affaire_num = 'AF{}0000'.format(code_year)

        if self.affaire_ind == '' or self.affaire_ind is None:
            l_affaires_sub = [t for t in l_affaires if t[0] == self.affaire_num]
            if len(l_affaires_sub) > 0:
                self.affaire_ind = '{0:0=3d}'.format(max([int(t[1]) for t in l_affaires_sub]) + 1)
            else:
                self.affaire_ind = '{0:0=3d}'.format(1)

        # Try to add and reset contact id if failed
        try:
            super(Affaire, self).add()

        except ValueError, e:
            self.affaire_num, self.affaire_ind = affaire_num_, affaire_ind_
            raise ValueError(e.message)

        return self

    @staticmethod
    def form_loading(step, index=None, data=None):
        if index is not None:
            l_index = [sch.name for sch in Affaire.l_index]
            d_index = {k: v for k, v in zip(l_index, index.split('/'))}
        else:
            d_index = None

        # Set filters for list choice
        filters = {}
        if step % Affaire.nb_step_form == 2:
            if data is not None and 'devis_id' in data.keys():
                rs = Devis.from_index_({'devis_id': data['devis_id']}).__getattribute__('designation_client')
                filters.update(
                    {'contact': {'designation': rs}, 'chantier': {'designation_client': rs}}
                )

        form_man = FormLoader(Affaire.l_index, Affaire.l_fields(widget=True, **filters))

        if step % Affaire.nb_step_form == 0:
            index_node = StringFields(
                title=u"Numéro d'affaire", name='index', missing=-1,
                l_choices=zip(Affaire.get_affaire(sep='/'), Affaire.get_affaire(sep='/')) + [('new', 'Nouveau')],
                desc=u"En cas de modification: choisir un numéro d'affaire et un numéro d'indice.\n"
                     u"En cas d'affaire secondaire: choisir le numéro d'affaire (peu import l'indice)")

            form_man.load_init_form(Affaire.action_field, index_node)

        else:
            if u'Ajouter une affaire secondaire' == data['action'] and 'affaire_num' not in data:
                data['affaire_num'] = d_index['affaire_num']

            data_db = None
            if d_index is not None:
                data_db = Affaire.from_index_(d_index).__dict__

            form_man.load(step % Affaire.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(type='html'):

        # Load database
        df = Affaire.load_db()

        table_man = TableLoader(Affaire.l_index, Affaire.l_fields(), limit=10, type=type)
        df, kwargs = table_man.load_reduce_table(df)
        d_footer = None

        return df, d_footer, kwargs
