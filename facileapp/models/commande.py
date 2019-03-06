# Global imports
import pandas as pd
from deform.widget import HiddenWidget

# Local import
from facile.core.fields import StringFields, FileFields, FloatFields, MoneyFields
from facile.core.form_loader import FormLoader
from facile.core.table_loader import TableLoader
from facile.core.base_model import BaseModel
from facileapp.models.affaire import Affaire
from facileapp.models.fournisseur import Fournisseur


class Commande(BaseModel):

    table_name = 'commande'
    l_index = [StringFields(title='Numero de Commande', name='commande_id', widget=HiddenWidget(), table_reduce=True,
                            rank=0, primary_key=True)]
    l_documents = [('comande', 'Resume de Commande')]
    l_actions = map(lambda x: (x.format('une commande'), x.format('une commande')), BaseModel.l_actions)
    action_field = StringFields(title='Action', name='action', l_choices=l_actions, round=0)
    nb_step_form = 2

    @staticmethod
    def l_fields(widget=False):
        if widget:
            l_fields = \
                [StringFields(title="Numero d'affaire", name='affaire_id', l_choices=Commande.list('affaire'),
                              table_reduce=True, rank=1, required=True),
                 StringFields(title='Fournisseur', name='raison_social', l_choices=Commande.list('fournisseur'),
                              table_reduce=True, rank=2, required=True),
                 MoneyFields(title='Montant Commande HT', name='montant_ht', required=True),
                 FloatFields(title='Taux TVA', name='taux_tva', l_choices=Commande.list('tva'), required=True),
                 MoneyFields(title='Montant TVA', name='montant_tva', widget=HiddenWidget()),
                 MoneyFields(title='Montant TTC', name='montant_ttc', widget=HiddenWidget(), table_reduce=True, rank=3),
                 FileFields(title="Details commande", name='details', required=True)]
        else:
            l_fields = \
                [StringFields(title="Numero d'affaire", name='affaire_id', table_reduce=True, rank=1, required=True),
                 StringFields(title='Fournisseur', name='raison_social', table_reduce=True, rank=2, required=True),
                 MoneyFields(title='Montant Commande HT', name='montant_ht', required=True),
                 FloatFields(title='Taux TVA', name='taux_tva', required=True),
                 MoneyFields(title='Montant TVA', name='montant_tva'),
                 MoneyFields(title='Montant TTC', name='montant_ttc', table_reduce=True, rank=3),
                 FileFields(title="Details commande", name='details', required=True)]

        return l_fields

    @staticmethod
    def declarative_base():
        return BaseModel.declarative_base(
            clsname='Commande', name=Commande.table_name, dbcols=[f.dbcol() for f in Commande.l_index + Commande.l_fields()]
        )

    @staticmethod
    def list(kw):

        if kw == 'fournisseur':
            return zip(Fournisseur.get_fournisseurs(), Fournisseur.get_fournisseurs())
        elif kw == 'affaire':
            return zip(Affaire.get_affaire(), map(str, Affaire.get_affaire()))
        elif kw == 'tva':
            return [(0.2, '20%'), (0.1, '10%'), (0.055, '5,5%'), (0.021, '2,1%')]
        else:
            return []

    @staticmethod
    def from_index_(d_index):
        # Series
        s = BaseModel.from_index('commande', d_index)
        return Commande(d_index, s.loc[[f.name for f in Commande.l_fields()]].to_dict())

    @staticmethod
    def load_db(**kwargs):
        l_fields = Commande.l_index + Commande.l_fields() + Commande.l_hfields

        # Load table
        df = BaseModel.load_db(table_name='commande', l_fields=l_fields, columns=kwargs.get('columns', None))

        return df

    @staticmethod
    def get_commande():
        return Commande.load_db(columns=['commande_id'])['commande_id'].unique()

    @staticmethod
    def merge_affaire(l_af):

        # Get main and sub affaire
        main = '/'.join([l_af[0].affaire_num, l_af[0].affaire_ind])
        sub = '/'.join([l_af[-1].affaire_num, l_af[-1].affaire_ind])

        # Load commande and update affaire id
        df = Commande.driver.select(Commande.table_name, **{"affaire_id": sub})
        df['affaire_id'] = main

        # Save changes
        Commande.driver.update_rows(df, Commande.table_name)

    def add(self):
        l_commandes = Commande.get_commande()

        # Save current contact id
        commande_id_ = self.commande_id

        if self.commande_id == '' or self.commande_id is None:
            self.commande_id = 'CM{0:0=4d}'.format(max(map(lambda x: int(x.replace('CM', '')), l_commandes)) + 1)

        self.montant_ttc, self.montant_tva = Commande.get_montant(
            self.__getattribute__('montant_ht'), self.__getattribute__('taux_tva')
        )

        # Try to add and reset conatct id if failed
        try:
            super(Commande, self).add()

        except ValueError, e:
            self.commande_id = commande_id_
            raise ValueError(e.message)

        return self

    def alter(self):

        self.montant_ttc, self.montant_tva = Commande.get_montant(
            self.__getattribute__('montant_ht'), self.__getattribute__('taux_tva')
        )

        super(Commande, self).alter()

        return self

    @staticmethod
    def get_montant(montant_ht, taux_tva):
        montant_tva = taux_tva * montant_ht
        return montant_tva + montant_ht, montant_tva

    @staticmethod
    def form_loading(step, index=None, data=None):

        if index is not None:
            d_index = {Commande.l_index[0].name: Commande.l_index[0].type(index)}
        else:
            d_index = None

        form_man = FormLoader(Commande.l_index, Commande.l_fields(widget=True))

        if step % Commande.nb_step_form == 0:
            index_node = StringFields(
                title='Numero de commande', name='index', missing=-1,
                l_choices=zip(Commande.get_commande(), Commande.get_commande()) + [('new', 'Nouveau')],
                desc="En cas de modification choisir un numero de commande",
            )
            form_man.load_init_form(Commande.action_field, index_node)

        else:
            data_db = None
            if d_index is not None:
                data_db = Commande.from_index_(d_index).__dict__

            form_man.load(step % Commande.nb_step_form, data_db=data_db, data_form=data)

        return form_man.d_form_data

    @staticmethod
    def table_loading(reduced=True, type='html', full_path=None):
        # Load database
        df = Commande.load_db()
        table_man = TableLoader(Commande.l_index, Commande.l_fields(), limit=10, type=type)

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
            table_man = TableLoader(Commande.l_index, Commande.l_fields())
            df, d_footer, kwargs = table_man.load_full_table(df)

        return df, d_footer, kwargs
