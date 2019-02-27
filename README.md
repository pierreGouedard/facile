# facile - multitask ERP

## Tables:

- ### employe:
    - **Form desc**: Rajouter les informations les employees de l'entreprise, suprimer / editer le profil d'un employe
    - **Primary key**: (prenom, nom)
    - **Other required fields**: categorie, securite_social, type_contrat, emploie, date_start, ville, adresse, code_postal, creation_date, maj_date
    - **Other facultative fields**: carte_sejoure, date_end, num_tel, mail

- ### fournisseur:
    - **Form desc**: Rajouter les informations sur les fournisseurs de l'entreprise, suprimer / editer le profil d'un fournisseur
    - **Primary key**: raison_sociale
    - **Other required fields**: adresse, ville, code_postal, maj_date, creation_date
    - **Other facultative fields**: cs_bp, num_tel, mail

- ### client:
    - **Form desc**: Rajouter les informations sur les clients de la boite, suprimer / editer le profil d'un client
    - **Primary key**: designation
    - **Other required fields**: raison_social, ville, adresse, code_postal, creation_date, maj_date
    - **Other facultative fields**: cs_bp, num_tel, mail

- ### contact:
    - **Form desc**: Rajouter un contact qualifié en dehors de l'entreprise, suprimer / editer le profil d'un contact
    - **Primary key**: contact_id
    - **Secondary key**: (designation, contact)
    - **Other required fields**: type, desc, maj_date, creation_date
    - **Other facultative fields**: cs_bp, adresse, ville, code_postal, num_tel, mail

- ### chantier:
    - **Form desc**: Rajouter un chantier pour un client donné, suprimer / editer le profil d'un contact
    - **Primary key**: chantier_id
    - **Secondary key**: (designation_client, nom)
    - **Other required fields**: , designation, desc, maj_date, creation_date
    - **Other facultative fields**: cs_bp, adresse, ville, code_postal, num_tel, mail

- ### affaire:
    - ** Form Desc**: Ouvrir une nouvelle affaire et l'assigner a un devis existant, suprimer / editer une affaire
    - **Primary key**: (affaire_num, affaire_ind)
    - **Other required fields**: devis_id, responsable, chantier_id, contact_chantier_client, contact_facturation_client, contact_chantier_interne, fae, maj_date, creation_date
    - **Other facultative fields**: 

- ### devis:
    - **Form desc**: Ouvrir un nouveau devis, suprimer / editer un devis
    - **Primary key**: devis_id
    - **Other required fields**: designation_client, contact_id, responsable, object, montant_achat, coef_achat, base_prix, date_start, date_end, creation_date, maj_date
    - **Other facultative fields**: heure_autre, heure_prod, prix_heure_autre, prix_heure_prod
    
- ### commande:
    - **Form desc**: Ouvrir une nouvelle demande d'achat rattaché a une affaire, suprimer / editer une demande d'achat
    - **Primary key**: comande_id
    - **Other required fields**: affaire_id, raison_social, montant_ht, taux_tva, montant_tva, montant_ttc, details, creation_date, maj_date
    - **Other facultative fields**:

- ### heure:
    - **Form desc**: Remplir les heures prod/autre pour chaque semaine, suprimer / editer les heures
    - **Primary key**: heure_id
    - **Other required fields**: affaire_id, semaine, name, heure_prod, heure_autre, creation_date, maj_date
    - **Other facultative fields**: carte_sejoure, date_end

- ### facture:
    - **Form desc**: Ouvrir une nouvelle demande de facture, suprimer / editer une demande de facture
    - **Primary key**: facture_id
    - **Other required fields**: affaire_id, type, montant_ht, situation, creation_date, maj_date
    - **Other facultative fields**: objet, date_visa, date_payed

## Organisation:

- page Forms: add / edit / delete records of main tables
- page Documents: download documents related to tables
- page Exportations: download excel version of tables
- page Controls: access to control app (data app)
- page admin (restricted): admin apps (user management, backup, cut-off ...)
