# facile
multitask ERP

Tables:

- employe:
    - Desc: Rajouter les informations les employees de l'entreprise, suprimer / editer le profil d'un employe
    - Primary key: (prenom, nom)
    - Other required fields: categorie, securite_social, type_contrat, emploie, date_start, ville, adresse, code_postal, creation_date, maj_date
    - Other facultative fields: carte_sejoure, date_end, num_tel, mail

- fournisseur:
    - Desc: Rajouter les informations sur les fournisseurs de l'entreprise, suprimer / editer le profil d'un fournisseur
    - Primary key: raison_sociale
    - Other required fields: adresse, ville, code_postal, maj_date, creation_date
    - Other facultative fields: cs_bp, num_tel, mail

- client:
    - Desc: Rajouter les informations sur les clients de la boite, suprimer / editer le profil d'un client
    - Primary key: designation
    - Other required fields: raison_social, ville, adresse, code_postal, creation_date, maj_date
    - Other facultative fields: cs_bp, num_tel, mail

- contact:
    - Desc: Rajouter un contact qualifié en dehors de l'entreprise, suprimer / editer le profil d'un contact
    - Primary key: contact_id
    - Secondary key: (designation, contact)
    - Other required fields: type, desc, maj_date, creation_date
    - Other facultative fields: cs_bp, adresse, ville, code_postal, num_tel, mail

- chantier:
    - Desc: Rajouter un chantier pour un client donné, suprimer / editer le profil d'un contact
    - Primary key: chantier_id
    - Secondary key: (designation_client, nom)
    - Other required fields: , designation, desc, maj_date, creation_date
    - Other facultative fields: cs_bp, adresse, ville, code_postal, num_tel, mail

- affaire:
    - Desc: Ouvrir une nouvelle affaire et l'assigner a un devis existant, suprimer / editer une affaire
    - Primary key: (affaire_num, affaire_ind)
    - Other required fields: devis_id, responsable, chantier_id, contact_chantier_client, contact_facturation_client, contact_chantier_interne, fae, maj_date, creation_date
    - Other facultative fields: 

- devis:
    - Desc: Ouvrir un nouveau devis, suprimer / editer un devis
    - Primary key: devis_id
    - Other required fields: designation_client, contact_id, responsable, object, montant_achat, coef_achat, base_prix, date_start, date_end, creation_date, maj_date

    - Other facultative fields: heure_autre, heure_prod, prix_heure_autre, prix_heure_prod
- commande:
    - Ouvrir une nouvelle demande d'achat rattaché a une affaire, suprimer / editer une demande d'achat
    - Primary key: (prenom, nom)
    - Other required fields: categorie, securite_social, type_contrat, emploie, date_start, ville, adresse, code_postal, num_tel, mail, creation_date, maj_date
    - Other facultative fields: carte_sejoure, date_end

- heure:
    - Ouvrir une nouvelle demande d'heure de travail, suprimer / editer une demande d'heure de travail
    - Primary key: (prenom, nom)
    - Other required fields: categorie, securite_social, type_contrat, emploie, date_start, ville, adresse, code_postal, num_tel, mail, creation_date, maj_date
    - Other facultative fields: carte_sejoure, date_end

- facture:
    - Ouvrir une nouvelle demande d'heure de travail, suprimer / editer une demande d'heure de travail
    - Primary key: (prenom, nom)
    - Other required fields: categorie, securite_social, type_contrat, emploie, date_start, ville, adresse, code_postal, num_tel, mail, creation_date, maj_date
    - Other facultative fields: carte_sejoure, date_end

Organisation:


- page Forms (add / edit / delete) main tables
    - list of options (left nav bar)
        * Personel: href = /form/personel
        * Affaires: href = /form/affaire
        * Devis: href = /form/devis
        * Achat: href = /form/achat
        * Heure: href = /form/Heure

    - Layout:
        * left navigtaion bar to move from one form to another
        * First row: main key of the table for search:
            * one editable field for creation (i.e str <affaire_id> + int <indice>
            * one dropdown list of existing affaire for edition
        * Middle rows: fill required information
            * A specific input for each information to fill in the corresponding table
        * Before last row:
            * A save, a delete and a 'get pdf' button
        * Last row:
            * table of the last 50 element created

- page Exploration
    - layout:
        * First row: search affaire
            * One dropdown list of existing affaire for edition
        * Second row: tables of all operation (Devis,  Achat, and Heure) associated with this affaire
            * tabulated tables with main information
        * Last row: export database
            * button export database.
