# Hôtel Manager — Système de Réservation

Application desktop de gestion hôtelière (chambres, clients, réservations, factures PDF).

## Stack
- Python 3.10+
- CustomTkinter (interface graphique moderne)
- SQLite (base de données locale, fichier `hotel.db` généré automatiquement)
- ReportLab (génération de factures PDF)

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

La base de données `hotel.db` est créée automatiquement au premier lancement, dans le dossier racine du projet.

## Structure du projet

```
hotel_app/
├── main.py                     # Point d'entrée
├── requirements.txt
├── database/
│   └── db_manager.py            # Connexion SQLite + création du schéma
├── models/                      # Accès aux données (1 classe par entité)
│   ├── chambre_model.py
│   ├── client_model.py
│   ├── reservation_model.py
│   └── facture_model.py
├── controllers/                 # Logique métier / validation (entre UI et modèles)
│   ├── chambre_controller.py
│   ├── client_controller.py
│   ├── reservation_controller.py
│   └── facture_controller.py
├── views/                       # Interface CustomTkinter
│   ├── main_window.py           # Fenêtre principale + sidebar
│   ├── chambres_view.py
│   ├── clients_view.py
│   ├── reservations_view.py
│   └── factures_view.py
├── utils/
│   ├── validators.py            # Validation email / téléphone / dates / prix
│   └── pdf_generator.py         # Génération de factures PDF (ReportLab)
├── assets/photos/               # Photos des chambres (copiées automatiquement)
└── invoices/                    # PDF des factures générées
```

## Fonctionnalités

### Module Chambres
- CRUD complet (ajout, modification, suppression)
- Attributs : numéro (unique), type (Simple/Double/Suite/VIP), prix/nuit, statut
  (Disponible/Occupée/Maintenance), description, photo
- Filtres combinés par type et par statut
- Le statut de la chambre est mis à jour automatiquement lors des réservations/annulations

### Module Clients
- CRUD complet : nom, prénom, téléphone, email, pièce d'identité, nationalité
- Recherche en temps réel (nom, prénom, téléphone, email)
- Historique complet des séjours (passés et en cours) par client

### Module Réservations
- Sélection client + chambre via menus déroulants
- Calcul automatique en temps réel : nombre de nuits et montant total
  (dès que les dates ou la chambre changent, avant même de valider)
- Vérification de disponibilité automatique : la chambre est bloquée si elle est
  déjà réservée sur une période qui chevauche les dates demandées
  (algorithme de chevauchement d'intervalles, pas juste une comparaison de statut)
- Actions : annulation (libère la chambre si plus aucune réservation active),
  check-out / clôture de séjour
- Génération de facture PDF en un clic depuis une réservation

### Module Factures
- Liste de toutes les factures générées, avec numéro unique (FAC-AAAAMMJJ-XXXX)
- Ouverture directe du PDF depuis l'application (Windows/Mac/Linux)

## Notes techniques
- Architecture en couches strictes : les vues ne parlent jamais directement à SQLite,
  toujours via un contrôleur qui valide les données puis appelle le modèle.
- `DatabaseManager` est un singleton : une seule connexion SQLite partagée par toute
  l'application, avec `PRAGMA foreign_keys = ON` pour l'intégrité référentielle.
- La vérification de disponibilité utilise la formule classique de chevauchement
  d'intervalles : `date_arrivee < date_depart_existante AND date_depart > date_arrivee_existante`,
  ce qui autorise les réservations contiguës (départ le jour de l'arrivée suivante).
