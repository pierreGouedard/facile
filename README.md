# facile
multitask ERP

Tables:

- Personel:
    - Desc: Rajouter les informations du personel de la boite, suprimer / editer le profil d'un membre du personel
    - Informations requises: Nom Prenom, poste, date d'entré dans l'entreprise, date de sortie de l'entreprise,
                             tarif heure
    - Nom champ:


- Affaires:
    - Desc: Ouvrir une nouvelle affaire et la rajouté a la base de donnée des affaires, suprimer / editer une affaire
    - Informations requises: Numero d'affaire, indice de l'affaire, chargé d'affaire, numero de devis associé (fac)

- Devis:
    - Desc: Ouvrir un nouveau devis, suprimer / editer un devis
    - Informations requises: Numero de devis, nombre d'heures, Montant achat
    - Nom champ:

- Achat:
    - Ouvrir une nouvelle demande d'achat rattaché a une affaire, suprimer / editer une demande d'achat
    - Informations requises: Numero de comande, Numréro d'affaire associé, Montant achat
    - Nom champ:

- Heure:
    - Ouvrir une nouvelle demande d'heure de travail, suprimer / editer une demande d'heure de travail
    - Informations requises: Numero de comande, Numréro d'affaire associé, nombre d'heure imputé, montant prévue (via
                             tarif heure de la table Personel)
    - Nom champ:


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
            * Middle rows: fill raquired information
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