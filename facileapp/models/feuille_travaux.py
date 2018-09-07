# Global import

# Local import
from facile.core.table_loader import TableLoader
from facileapp.models.devis import Devis
from facileapp.models.affaire import Affaire
from facileapp.models.facture import Facture
from facileapp.models.commande import Commande
from facileapp.models.heure import Heure


class BaseView(object):
    main_model = []
    l_models = []

    @staticmethod
    def load_view():
        raise NotImplementedError


class FeuilleTravaux(BaseView):
    main_model = Affaire
    l_models = [Affaire,  Devis, Facture, Commande, Heure]

    @staticmethod
    def load_view():
        # Load affaire db
        df = Affaire.load_db()

        # Join devis information
        df_devis = Devis.load_db()
        df_devis = df_devis.rename(columns={c: '{}_devis'.format(c) for c in df_devis.columns
                                            if c not in ['devis_id', 'creation_date', 'maj_date']})

        df = df.merge(df_devis[[c for c in df_devis.columns if c not in ['creation_date', 'maj_date']]],
                      on='devis_id', how='left')

        # Join billing information
        df_facture = Facture.load_db()

        df_facture_ = df_facture[['affaire_id', 'montant_ttc']]\
            .groupby(['affaire_id'])\
            .sum()\
            .rename(columns={'montant_ttc': 'montant_facture'})\
            .reset_index()

        df = df.merge(df_facture_, on='affaire_id', how='left')
        df = df.fillna({'montant_facture': 0.0})

        df_encaisse = df_facture[['affaire_id', 'is_payed', 'montant_ttc']]\
            .groupby(['affaire_id', 'is_payed'])\
            .sum()\
            .rename(columns={'montant_ttc': 'montant_encaisse'})\
            .reset_index(level=0)\
            .loc['yes', :]\
            .reset_index(drop=True)

        df = df.merge(df_encaisse, on='affaire_id', how='left')
        df = df.fillna({'montant_encaisse': 0.0})

        # Join command information
        df_commande = Commande.load_db()
        df_commande = df_commande[['affaire_id', 'montant_ttc']]\
            .groupby(['affaire_id'])\
            .sum()\
            .rename(columns={'montant_ttc': 'montant_commande'})\
            .reset_index()
        df = df.merge(df_commande, on='affaire_id', how='left')
        df = df.fillna({'montant_commande': 0.0})

        # Join heures information
        df_heure = Heure.load_db()
        df_heure = df_heure[['affaire_id', 'nb_heure_be', 'nb_heure_ch']]\
            .groupby(['affaire_id'])\
            .sum()\
            .rename(columns={'nb_heure_be': 'nb_heure_be_provided', 'nb_heure_ch': 'nb_heure_ch_provided'})\
            .reset_index()

        df = df.merge(df_heure, on='affaire_id', how='left')
        df = df.fillna({'nb_heure_be_provided': 0.0, 'nb_heure_ch_provided': 0.0})

        return df

    @staticmethod
    def table_loading():
        l_index = FeuilleTravaux.main_model.l_index
        l_fields = FeuilleTravaux.main_model.l_fields()

        # Load database
        df = FeuilleTravaux.load_view()

        l_model_cols = [f.name for f in l_index + l_fields]
        l_extra_cols = [c for c in df.columns if c not in l_model_cols]
        table_man = TableLoader(l_index, l_fields)
        df, d_footer, kwargs = table_man.load_full_table(df, l_extra_cols=l_extra_cols)

        return df, d_footer, kwargs

    @staticmethod
    def document_loading():
        raise NotImplementedError