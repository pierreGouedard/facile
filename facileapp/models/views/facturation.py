# Global import

# Local import
from facile.core.fields import StringFields
from facile.utils.drivers.files import FileDriver
from facile.core.document_generator import WordDocument
from facileapp.models.views.base_view import BaseView
from facileapp.models.devis import Devis
from facileapp.models.affaire import Affaire
from facileapp.models.facture import Facture
from facileapp.models.contact import Contact


class Facturation(BaseView):
    l_documents = [('detail_facture', 'Detail facture')]
    main_model = Facture
    l_models = [Affaire,  Devis]

    @staticmethod
    def load_view():
        # Load affaire db
        df = Facture.load_db()
        df['affaire_num'] = df.affaire_id.apply(lambda x: x.split('/')[0])
        df['affaire_ind'] = df.affaire_id.apply(lambda x: x.split('/')[1])

        # Join devis information
        df_devis = Devis.load_db()
        df_devis = df_devis[['devis_id', 'designation_client', 'object', 'price', 'date_start', 'date_end', 'base_prix']]

        df_info = Affaire.load_db()
        df_info = df_info[['affaire_num', 'affaire_ind', 'devis_id', 'contact_facturation_client', 'responsable', 'fae']]\
            .merge(df_devis, on='devis_id', how='left')

        # Join info to billing table
        df = df.merge(df_info, on=['affaire_num', 'affaire_ind'], how='left')

        return df

    @staticmethod
    def form_document_loading():

        index_node = StringFields(
            title='Numero de facture', name='index', l_choices=zip(Facture.get_facture(), Facture.get_facture())
        )
        document_node = StringFields(
            title='Nom document', name='document', l_choices=Facturation.l_documents
        )

        return {'nodes': [document_node.sn, index_node.sn]}

    @staticmethod
    def document_(index, path, driver=FileDriver('doc_fact', ''), name='doc_fact.docx'):

        df = Facturation.load_view()
        df = df.loc[df[Facture.l_index[0].name] == index[Facture.l_index[0].name]]
        df_contact = Contact.load_db()
        s_contact = df_contact.loc[df_contact.contact_id == df['contact_facturation_client'].iloc[0]].iloc[0]

        word_document = WordDocument(path, driver, {})

        title = 'FACTURE {}'.format(index[Facture.l_index[0].name])
        word_document.add_title(title, font_size=15, text_align='center', color='000000')

        # Info affaire
        word_document.add_title('Details Affaire', font_size=12, text_align='left', color='000000', space_before=1.)
        word_document.add_field(
            "Numero d'affaire", '{}/{}'.format(df['affaire_num'].iloc[0], df['affaire_ind'].iloc[0]), left_indent=0.15,
            space_before=0.1
        )
        word_document.add_field('Designation client', df['designation_client'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Objet du devis', df['object'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Montant du devis', df['price'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Objet du devis', df['object'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Debut du chantier', df['date_start'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Fin du chantier', df['date_end'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Base de prix', df['base_prix'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Responsable affaire', df['responsable'].iloc[0], left_indent=0.15, space_before=0.1)

        # Info facture
        word_document.add_title('Infos facture', font_size=12, text_align='left', color='000000', space_before=1.)
        word_document.add_field(
            'Montant facture HT', '{} Euros'.format(float(int(df['montant_ht'].iloc[0] * 100) / 100)), left_indent=0.15,
            space_before=0.1
        )
        word_document.add_field('Numero de situation', df['situation'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Date de visa', df['date_visa'].iloc[0], left_indent=0.15, space_before=0.1)
        word_document.add_field('Date de paiement', df['date_payed'].iloc[0], left_indent=0.15, space_before=0.1)

        coord = '{}, {} - {} {}'.format(
            s_contact['adresse'], s_contact['cs_bp'], s_contact['code_postal'], s_contact['ville']
        )
        word_document.add_simple_paragraph(
            ['Adresse de facturation'], space_before=0.1, space_after=0.1, left_indent=0.15, bold=True
        )
        word_document.add_simple_paragraph(
            [s_contact['designation'], s_contact['contact'], coord], break_run=True, space_before=0.4,
            alignment='center'
        )

        # Save document
        word_document.save_document(name)


