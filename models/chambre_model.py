"""
Modèle Chambre : encapsule toutes les opérations SQL liées aux chambres.
"""

from database.db_manager import DatabaseManager


class Chambre:
    def __init__(self, id=None, numero="", type="Simple", prix_nuit=0.0,
                 statut="Disponible", description="", photo_path=None):
        self.id = id
        self.numero = numero
        self.type = type
        self.prix_nuit = prix_nuit
        self.statut = statut
        self.description = description
        self.photo_path = photo_path

    @staticmethod
    def _from_row(row):
        if row is None:
            return None
        return Chambre(
            id=row["id"], numero=row["numero"], type=row["type"],
            prix_nuit=row["prix_nuit"], statut=row["statut"],
            description=row["description"], photo_path=row["photo_path"]
        )

    @classmethod
    def create(cls, numero, type, prix_nuit, statut, description, photo_path=None):
        db = DatabaseManager()
        cur = db.execute(
            """INSERT INTO chambres (numero, type, prix_nuit, statut, description, photo_path)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (numero, type, prix_nuit, statut, description, photo_path)
        )
        return cur.lastrowid

    @classmethod
    def update(cls, id, numero, type, prix_nuit, statut, description, photo_path=None):
        db = DatabaseManager()
        db.execute(
            """UPDATE chambres
               SET numero=?, type=?, prix_nuit=?, statut=?, description=?, photo_path=?
               WHERE id=?""",
            (numero, type, prix_nuit, statut, description, photo_path, id)
        )

    @classmethod
    def delete(cls, id):
        db = DatabaseManager()
        db.execute("DELETE FROM chambres WHERE id=?", (id,))

    @classmethod
    def get_by_id(cls, id):
        db = DatabaseManager()
        row = db.fetchone("SELECT * FROM chambres WHERE id=?", (id,))
        return cls._from_row(row)

    @classmethod
    def get_all(cls, type_filter=None, statut_filter=None):
        db = DatabaseManager()
        query = "SELECT * FROM chambres WHERE 1=1"
        params = []
        if type_filter and type_filter != "Tous":
            query += " AND type=?"
            params.append(type_filter)
        if statut_filter and statut_filter != "Tous":
            query += " AND statut=?"
            params.append(statut_filter)
        query += " ORDER BY numero"
        rows = db.fetchall(query, tuple(params))
        return [cls._from_row(r) for r in rows]

    @classmethod
    def update_statut(cls, id, statut):
        db = DatabaseManager()
        db.execute("UPDATE chambres SET statut=? WHERE id=?", (statut, id))

    @classmethod
    def numero_exists(cls, numero, exclude_id=None):
        db = DatabaseManager()
        if exclude_id:
            row = db.fetchone(
                "SELECT id FROM chambres WHERE numero=? AND id != ?",
                (numero, exclude_id)
            )
        else:
            row = db.fetchone("SELECT id FROM chambres WHERE numero=?", (numero,))
        return row is not None
