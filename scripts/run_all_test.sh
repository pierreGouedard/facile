#!/bin/bash

python -m unittest tests.models.affaire.TestAffaire.test_basic
python -m unittest tests.models.affaire.TestAffaire.test_request
python -m unittest tests.models.base_prix.TestBasePrix.test_request
python -m unittest tests.models.chantier.TestChantier.test_basic
python -m unittest tests.models.chantier.TestChantier.test_request
python -m unittest tests.models.client.TestClient.test_basic
python -m unittest tests.models.client.TestClient.test_request
python -m unittest tests.models.commande.TestCommande.test_basic
python -m unittest tests.models.commande.TestCommande.test_request
python -m unittest tests.models.contact.TestContact.test_basic
python -m unittest tests.models.contact.TestContact.test_request
python -m unittest tests.models.devis.TestDevis.test_basic
python -m unittest tests.models.devis.TestDevis.test_request
python -m unittest tests.models.employe.TestEmploye.test_basic
python -m unittest tests.models.employe.TestEmploye.test_request
python -m unittest tests.models.facture.TestFacture.test_basic
python -m unittest tests.models.facture.TestFacture.test_request
python -m unittest tests.models.fournisseur.TestFournisseur.test_basic
python -m unittest tests.models.fournisseur.TestFournisseur.test_request
