#!/usr/bin/python
# -*- coding: utf-8 -*-

# Global import

# Local import
from facile.core.fields import StringFields
from facile.utils.drivers.files import FileDriver
from facile.core.document_generator import WordDocument
from facileapp.models.views.base_view import BaseView
from facileapp.models.devis import Devis
from facileapp.models.affaire import Affaire
from facileapp.models.commande import Commande
from facileapp.models.contact import Contact
from facileapp.models.chantier import Chantier


class Achat(BaseView):
    l_documents = [(u'detail_commande', u'Détails Commande')]
    main_model = Commande
    l_models = [Affaire,  Devis]

    @staticmethod
    def load_view():
        # Load affaire db
        df = Commande.load_db()
        df['affaire_num'] = df.affaire_id.apply(lambda x: x.split('/')[0])
        df['affaire_ind'] = df.affaire_id.apply(lambda x: x.split('/')[1])

        # Join devis information
        df_devis = Devis.load_db()
        df_devis = df_devis[['devis_id', 'designation_client', 'object', 'date_start', 'date_end', 'base_prix',
                             'montant_achat', 'coef_achat']]

        df_info = Affaire.load_db()
        df_info = df_info[
            ['affaire_num', 'affaire_ind', 'devis_id', 'responsable', 'contact_chantier_interne',
             'contact_chantier_client', 'chantier_id']
        ].merge(df_devis, on='devis_id', how='left')

        # Join info to command table
        df = df.merge(df_info, on=['affaire_num', 'affaire_ind'], how='left')

        return df

    @staticmethod
    def form_document_loading():

        index_node = StringFields(
            title=u'Numero de facture', name='index', l_choices=zip(Commande.get_commande(), Commande.get_commande())
        )
        document_node = StringFields(
            title=u'Nom document', name='document', l_choices=Achat.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

    @staticmethod
    def document_(index, path, driver=FileDriver('doc_fact', ''), name='doc_fact.docx'):

        df = Achat.load_view()
        df = df.loc[df[Commande.l_index[0].name] == index[Commande.l_index[0].name]]

        df_contact = Contact.load_db()
        df_chantier = Chantier.load_db()

        word_document = WordDocument(path, driver, {})

        title = u'COMMANDE {}'.format(index[Commande.l_index[0].name])
        word_document.add_title(title, font_size=15, text_align='center', color='000000')

        # Info affaire
        word_document.add_title(u'Détails Affaire', font_size=12, text_align='left', color='000000', space_before=1.)
        word_document.add_field(
            u"Numero d'affaire", u'{}/{}'.format(df['affaire_num'].iloc[0], df['affaire_ind'].iloc[0]), left_indent=0.15,
            space_before=0.1
        )
        word_document.add_field(u'Désignation client', df['designation_client'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Objet du devis', df['object'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Montant achat devis', df['responsable'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Début du chantier', df['date_start'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Fin du chantier', df['date_end'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Base de prix', df['base_prix'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field(u'Responsable affaire', df['responsable'].iloc[0], left_indent=0.15, space_before=0.1)

        # Info Chantier
        s_chantier = df_chantier.loc[df_chantier['chantier_id'] == df['chantier_id'].iloc[0]].iloc[0]
        contact_client_ch = df['contact_chantier_client'].iloc[0]
        designation = df_contact.loc[df_contact.contact_id == contact_client_ch, 'contact'].iloc[0]

        word_document.add_title(u'Info Chantier', font_size=12, text_align='left', color='000000', space_before=1.)
        word_document.add_field(
            u'Adresse', u'{}, {} {}'.format(
            s_chantier['adresse'], s_chantier['code_postal'], s_chantier['ville']
            ), left_indent=0.15
        )
        word_document.add_field(
            u'Responsable chantier interne', df['contact_chantier_interne'].iloc[0], left_indent=0.15
        )
        word_document.add_field(
            u'Responsable chantier client', u'{} ({})'.format(contact_client_ch, designation), left_indent=0.15
        )

        word_document.add_title(u'Info Commande', font_size=12, text_align='left', color='000000', space_before=1.)
        word_document.add_field(
            u'Montant Commande HT', u'{} Euros'.format(float(int(df['montant_ht'].iloc[0] * 100) / 100)),
            left_indent=0.15, space_before=0.1
        )

        # Save document
        word_document.save_document(name)


