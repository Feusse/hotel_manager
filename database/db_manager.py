# FICHIER: db_manager.py
"""
Gestion centralisée de la connexion SQLite.
Singleton simple : une seule connexion partagée par toute l'application.
"""

import sqlite3
import os

DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DB_DIR, "hotel.db")


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS chambres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('Simple', 'Double', 'Suite', 'VIP')),
            prix_nuit REAL NOT NULL,
            statut TEXT NOT NULL DEFAULT 'Disponible'
                CHECK(statut IN ('Disponible', 'Occupée', 'Maintenance')),
            description TEXT,
            photo_path TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT,
            email TEXT,
            piece_identite TEXT,
            nationalite TEXT,
            date_creation TEXT DEFAULT (datetime('now'))
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            chambre_id INTEGER NOT NULL,
            date_arrivee TEXT NOT NULL,
            date_depart TEXT NOT NULL,
            nb_nuits INTEGER NOT NULL,
            montant_total REAL NOT NULL,
            statut TEXT NOT NULL DEFAULT 'Confirmée'
                CHECK(statut IN ('Confirmée', 'Annulée', 'Terminée')),
            date_creation TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
            FOREIGN KEY (chambre_id) REFERENCES chambres(id) ON DELETE RESTRICT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reservation_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            montant REAL NOT NULL,
            date_depense TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reservation_id INTEGER NOT NULL,
            numero_facture TEXT NOT NULL UNIQUE,
            date_emission TEXT DEFAULT (datetime('now')),
            montant_total REAL NOT NULL,
            chemin_pdf TEXT,
            FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
        );
        """)

        self.conn.commit()

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur

    def fetchall(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def fetchone(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def close(self):
        self.conn.close()
        