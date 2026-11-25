"""
Modèle Facture : traçabilité des factures générées (indépendant du PDF lui-même).
"""

from datetime import datetime
from database.db_manager import DatabaseManager


class Facture:
    def __init__(self, id=None, reservation_id=None, numero_facture="",
                 date_emission=None, montant_total=0.0, chemin_pdf=None):
        self.id = id
        self.reservation_id = reservation_id
        self.numero_facture = numero_facture
        self.date_emission = date_emission
        self.montant_total = montant_total
        self.chemin_pdf = chemin_pdf

    @staticmethod
    def _from_row(row):
        if row is None:
            return None
        return Facture(
            id=row["id"], reservation_id=row["reservation_id"],
            numero_facture=row["numero_facture"], date_emission=row["date_emission"],
            montant_total=row["montant_total"], chemin_pdf=row["chemin_pdf"]
        )

    @classmethod
    def generer_numero(cls):
        """Génère un numéro de facture unique du type FAC-20260705-0001."""
        db = DatabaseManager()
        today = datetime.now().strftime("%Y%m%d")
        row = db.fetchone(
            "SELECT COUNT(*) as cnt FROM factures WHERE numero_facture LIKE ?",
            (f"FAC-{today}-%",)
        )
        seq = (row["cnt"] if row else 0) + 1
        return f"FAC-{today}-{seq:04d}"

    @classmethod
    def create(cls, reservation_id, montant_total, chemin_pdf):
        db = DatabaseManager()
        numero = cls.generer_numero()
        cur = db.execute(
            """INSERT INTO factures (reservation_id, numero_facture, montant_total, chemin_pdf)
               VALUES (?, ?, ?, ?)""",
            (reservation_id, numero, montant_total, chemin_pdf)
        )
        return cur.lastrowid, numero

    @classmethod
    def get_by_reservation(cls, reservation_id):
        db = DatabaseManager()
        row = db.fetchone(
            "SELECT * FROM factures WHERE reservation_id=? ORDER BY id DESC LIMIT 1",
            (reservation_id,)
        )
        return cls._from_row(row)

    @classmethod
    def get_all(cls):
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT f.*, r.date_arrivee, r.date_depart,
                      cl.nom AS client_nom, cl.prenom AS client_prenom
               FROM factures f
               JOIN reservations r ON f.reservation_id = r.id
               JOIN clients cl ON r.client_id = cl.id
               ORDER BY f.date_emission DESC"""
        )
        return rows
