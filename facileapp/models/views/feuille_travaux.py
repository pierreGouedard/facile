# Global import
import pandas as pd

# Local import
from facile.core.fields import StringFields
from facile.core.document_generator import WordDocument
from facile.core.table_loader import TableLoader
from facileapp.models.views.base_view import BaseView
from facileapp.models.client import Client
from facileapp.models.chantier import Chantier
from facileapp.models.contact import Contact
from facileapp.models.devis import Devis
from facileapp.models.affaire import Affaire
from facileapp.models.facture import Facture
from facileapp.models.commande import Commande
from facileapp.models.heure import Heure


class FeuilleTravaux(BaseView):
    l_documents = [('feuille_travaux', 'Feuille de travaux')]
    main_model = Affaire
    l_models = [Affaire,  Devis, Facture, Commande, Heure]
    l_main_index = [f.name for f in Affaire.l_index]

    @staticmethod
    def merge_to_main(df_main, df_sub, l_col_sub, d_fillna=None):

        l_col_main = FeuilleTravaux.l_main_index

        df_sub = df_sub[l_col_main + l_col_sub] \
            .groupby(l_col_main) \
            .sum() \
            .reset_index()

        df_main = df_main.merge(df_sub, on=l_col_main, how='left')

        if d_fillna is None:
            d_fillna = {c: 0.0 for c in l_col_sub}

        df_main = df_main.fillna(d_fillna)

        return df_main

    @staticmethod
    def split_main_indices(df):
        df['affaire_num'] = df.affaire_id.apply(lambda x: x.split('-')[0])
        df['affaire_ind'] = df.affaire_id.apply(lambda x: x.split('-')[1])

        return df

    @staticmethod
    def load_view(return_cols=True):

        # Load affaire db
        df = Affaire.load_db()
        l_models_cols = []

        # Join devis information
        df_devis = Devis.load_db()
        df_devis = df_devis[[c for c in df_devis.columns if c not in ['creation_date', 'maj_date']]]
        df_devis = df_devis.rename(columns={c: '{}_devis'.format(c) for c in df_devis.columns if c != 'devis_id'})
        df = df.merge(df_devis, on='devis_id', how='left')

        l_models_cols += [c for c in df_devis.columns if c != 'devis_id']

        # Load billing and Build affaire index
        df_facture = Facture.load_db()
        df_facture = FeuilleTravaux.split_main_indices(df_facture)

        # For each situation join amount factured
        for i in range(1, 13):
            df_facture_ = df_facture.loc[df_facture['situation'] == i]\
                .rename(columns={'montant_ht': 'montant_situation_{}'.format(i)})
            df = FeuilleTravaux.merge_to_main(df, df_facture_, ['montant_situation_{}'.format(i)])
            l_models_cols += ['montant_situation_{}'.format(i)]

        # Join command information
        df_commande = Commande.load_db()
        df_commande = FeuilleTravaux.split_main_indices(df_commande)

        df = FeuilleTravaux\
            .merge_to_main(
                df, df_commande.rename(columns={'montant_ht': 'montant_total_commande'}), ['montant_total_commande']
            )

        l_models_cols += ['montant_total_commande']

        # Load hours information
        df_heure = Heure.load_db()
        df_heure = FeuilleTravaux.split_main_indices(df_heure)

        # Heures non interimaires
        df_heure_ = df_heure.loc[df_heure['name'] != 'interim']\
            .rename(columns={'heure_prod': 'heure_prod_saisie', 'heure_autre': 'heure_autre_saisie'})
        df = FeuilleTravaux.merge_to_main(df, df_heure_, ['heure_prod_saisie', 'heure_autre_saisie'])

        # Heures interimaires
        df_heure_ = df_heure.loc[df_heure['name'] == 'interim']\
            .rename(columns={'heure_prod': 'heure_prod_saisie_interim', 'heure_autre': 'heure_autre_saisie_interim'})
        df = FeuilleTravaux.merge_to_main(df, df_heure_, ['heure_prod_saisie_interim', 'heure_autre_saisie_interim'])

        l_models_cols += ['heure_prod_saisie', 'heure_autre_saisie', 'heure_prod_saisie_interim',
                          'heure_autre_saisie_interim']

        if return_cols:
            return df, l_models_cols

        return df

    @staticmethod
    def table_loading(type='html', full_path=None):
        l_index = FeuilleTravaux.main_model.l_index
        l_fields = FeuilleTravaux.main_model.l_fields()

        # Load database
        df, l_model_cols = FeuilleTravaux.load_view(return_cols=True)
        table_man = TableLoader(l_index, l_fields, type=type)

        if type == 'excel':

            # Get processed table
            df = table_man.load_full_table(df, l_extra_cols=l_model_cols)

            # Save excel file
            writer = pd.ExcelWriter(full_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Feuille1', index=False)
            writer.save()

            return

        l_model_cols = [f.name for f in l_index + l_fields]
        l_extra_cols = [c for c in df.columns if c not in l_model_cols]
        table_man = TableLoader(l_index, l_fields)
        df, d_footer, kwargs = table_man.load_full_table(df, l_extra_cols=l_extra_cols)

        return df, d_footer, kwargs

    @staticmethod
    def form_document_loading():

        index_node = StringFields(
            title="Numero d'affaire", name='index', l_choices=zip(Affaire.get_affaire(), Affaire.get_affaire())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=FeuilleTravaux.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

    @staticmethod
    def document_(index, path, driver, name='doc_fdt.docx'):
        df, _ = FeuilleTravaux.load_view()
        df = df.loc[
            df[[f.name for f in Affaire.l_index]].apply(lambda r: all([r[c] == index[c] for c in r.index]), axis=1)
        ]

        # Load contact
        df_contact = Contact.load_db()

        # Load client
        df_client = Client.load_db()

        # Load chantier
        df_chantier = Chantier.load_db()

        word_document = WordDocument(path, driver, {'top_margin': 0.5})

        # Document title
        title = 'Feuille de travaux {}'.format('/'.join(df[FeuilleTravaux.l_main_index].values[0]))
        word_document.add_title(title, font_size=15, text_align='center', color='000000')

        # CLIENT
        s_client = df_client.loc[df_client.designation == df['designation_client_devis'].iloc[0]].iloc[0]

        word_document.add_title('Client', font_size=12, text_align='left', color='000000')
        word_document.add_field('Designation', s_client['designation'], left_indent=0.15)
        word_document.add_field('Raison sociale', s_client['raison_social'], left_indent=0.15)
        word_document.add_field(
            'Adresse', value='{}, {} - {} {}'.format(
                s_client['adresse'], s_client['cs_bp'], s_client['code_postal'], s_client['ville']
            ),
            left_indent=0.15
        )
        s_contact = df_contact.loc[df_contact.contact_id == df['contact_id_devis'].iloc[0]].iloc[0]
        word_document.add_field(
            'Responsable commande',
            '{} ({})'.format(s_contact['contact_id'], s_contact['contact']),
            left_indent=0.15, space_before=0.1
        )
        # DEVIS
        word_document.add_title('Devis', font_size=12, text_align='left', color='000000')

        word_document.add_field('Numero', df['devis_id'].iloc[0], left_indent=0.15)
        word_document.add_field('Objet', df['object_devis'].iloc[0], left_indent=0.15)
        word_document.add_field('Responsable devis', df['responsable_devis'].iloc[0], left_indent=0.15)
        word_document.add_field('Date de debut', df['date_start_devis'].iloc[0], left_indent=0.15)
        word_document.add_field('Date de fin', df['date_end_devis'].iloc[0], left_indent=0.15)
        word_document.add_field('Montant total du devis', '{} euros'.format(df['price_devis'].iloc[0]), left_indent=0.15)
        word_document.add_simple_paragraph(
            ['Details'], space_before=0.06, space_after=0.06, left_indent=0.15, bold=True
        )

        l_values = [[df['heure_prod_devis'].iloc[0], df['prix_heure_prod_devis'].iloc[0],
                     df['heure_autre_devis'].iloc[0], df['prix_heure_autre_devis'].iloc[0],
                     df['montant_achat_devis'].iloc[0], df['coef_achat_devis'].iloc[0]]]

        df_table = pd.DataFrame(
            l_values, columns=['Heures Prod', 'Prix Heures Prod', 'Heures Autres', 'Prix Heures Autres',
                               'Montant achat', 'Coef achat']
        )

        word_document.add_table(df_table, index_column=-1, left_indent=0.15)

        # CHANTIER
        s_chantier = df_chantier.loc[df_chantier['chantier_id'] == df['chantier_id'].iloc[0]].iloc[0]
        contact_client_ch = df['contact_chantier_client'].iloc[0]
        designation = df_contact.loc[df_contact.contact_id == contact_client_ch, 'contact'].iloc[0]

        word_document.add_title('Chantier', font_size=12, text_align='left', color='000000')
        word_document.add_field(
            'Adresse', '{}, {} {}'.format(
            s_chantier['adresse'], s_chantier['code_postal'], s_chantier['ville']
            ), left_indent=0.15
        )
        word_document.add_field('Responsable interne', df['contact_chantier_interne'].iloc[0], left_indent=0.15)
        word_document.add_field(
            'Responsable client', '{} ({})'.format(contact_client_ch, designation), left_indent=0.15
        )

        # SUIVI
        heure_prod = df['heure_prod_saisie'].sum() + df['heure_prod_saisie_interim'].sum()
        heure_autre = df['heure_autre_saisie'].sum() + df['heure_autre_saisie_interim'].sum()
        montant_achat = df['montant_total_commande'].sum()

        word_document.add_title('Suivi', font_size=12, text_align='left', color='000000')

        l_values = [["REALISE", heure_prod, heure_autre, montant_achat],
                    ["ECART DEVIS", heure_prod - df['heure_prod_devis'].sum(),
                     heure_autre - df['heure_autre_devis'].sum(),
                     montant_achat - df['montant_achat_devis'].sum()]]

        df_table = pd.DataFrame(l_values, columns=[' ', 'Heures prod', 'Heures autre', 'Achat'])

        word_document.add_table(df_table, index_column=0, left_indent=0.15)

        # FACTURATION
        s_contact = df_contact.loc[df_contact.contact_id == df['contact_facturation_client'].iloc[0]].iloc[0]
        coord = '{}, {} - {} {}'.format(
            s_contact['adresse'], s_contact['cs_bp'], s_contact['code_postal'], s_contact['ville']
        )
        word_document.add_title('Facturation', font_size=12, text_align='left', color='000000')
        word_document.add_simple_paragraph(
            [s_contact['designation'], s_contact['contact'], coord], break_run=True, space_before=0.06,
            alignment='center'
        )

        l_values = [['Visa'] + [str('__/__/____')] * 6, ['Encaissement'] + [str('__/__/____')] * 6]
        df_table = pd.DataFrame(
            l_values, columns=['Situation'] + ['{}'.format(i + 1) for i in range(6)]
        )
        word_document.add_table(df_table, index_column=0, left_indent=0.15)

        l_values = [['Visa'] + [str('__/__/____')] * 6, ['Encaissement'] + [str('__/__/____')] * 6]

        df_table = pd.DataFrame(
            l_values, columns=['Situation'] + ['{}'.format(i + 7) for i in range(6)]
        )
        word_document.add_table(df_table, index_column=0, left_indent=0.15)

        # Save document
        word_document.save_document(name)

    @staticmethod
    def control_loading():
        # May be have a view of case sold out, case running
        d_control_data = {}
        df, _ = FeuilleTravaux.load_view()

        # App 1 repartition categorie among employes
        df['montant_facture'] = df[[c for c in df.columns if 'montant_situation_' in c]].sum(axis=1)
        df['state'] = df[['price_devis', 'montant_facture']]\
            .apply(lambda row: 'cloturee' if abs(row['price_devis'] - row['montant_facture']) < 10 else 'En cours',
                   axis=1)

        df_ca = df[['price_devis', 'state']].groupby('state')\
            .sum()\
            .reset_index()\
            .rename(columns={'state': 'name', 'price_devis': 'value'})

        df_ca['hover'] = df['price_devis'].apply(lambda x: '{:,.2f} Euros'.format(float(int(x * 100) / 100)))

        d_control_data['repca'] = {
            'plot': {'k': 'pie', 'd': df_ca, 'o': {'hover': True}},
            'rows': [('title', [{'content': 'title', 'value': "Chiffre d'affaire cloture et en cours", 'cls': 'text-center'}]),
                     ('figure', [{'content': 'plot'}])],
            'rank': 0
                }
        return d_control_data
