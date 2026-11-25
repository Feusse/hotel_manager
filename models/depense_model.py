# FICHIER: depense_model.py
"""
Modèle Dépense : dépenses annexes d'un client durant son séjour
(minibar, restaurant, spa, blanchisserie, etc.), rattachées à une réservation.
"""

from database.db_manager import DatabaseManager


class Depense:
    def __init__(self, id=None, reservation_id=None, description="",
                 montant=0.0, date_depense=None):
        self.id = id
        self.reservation_id = reservation_id
        self.description = description
        self.montant = montant
        self.date_depense = date_depense

    @staticmethod
    def _from_row(row):
        if row is None:
            return None
        return Depense(
            id=row["id"], reservation_id=row["reservation_id"],
            description=row["description"], montant=row["montant"],
            date_depense=row["date_depense"]
        )

    @classmethod
    def create(cls, reservation_id, description, montant):
        db = DatabaseManager()
        cur = db.execute(
            """INSERT INTO depenses (reservation_id, description, montant)
               VALUES (?, ?, ?)""",
            (reservation_id, description, montant)
        )
        return cur.lastrowid

    @classmethod
    def delete(cls, id):
        db = DatabaseManager()
        db.execute("DELETE FROM depenses WHERE id=?", (id,))

    @classmethod
    def get_by_reservation(cls, reservation_id):
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT * FROM depenses WHERE reservation_id=? ORDER BY date_depense""",
            (reservation_id,)
        )
        return [cls._from_row(r) for r in rows]

    @classmethod
    def get_total_by_reservation(cls, reservation_id):
        db = DatabaseManager()
        row = db.fetchone(
            "SELECT COALESCE(SUM(montant), 0) AS total FROM depenses WHERE reservation_id=?",
            (reservation_id,)
        )
        return row["total"] if row else 0.0
        
        