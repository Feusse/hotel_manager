"""
Modèle Client : opérations SQL liées aux clients + historique des séjours.
"""

from database.db_manager import DatabaseManager


class Client:
    def __init__(self, id=None, nom="", prenom="", telephone="", email="",
                 piece_identite="", nationalite="", date_creation=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.email = email
        self.piece_identite = piece_identite
        self.nationalite = nationalite
        self.date_creation = date_creation

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @staticmethod
    def _from_row(row):
        if row is None:
            return None
        return Client(
            id=row["id"], nom=row["nom"], prenom=row["prenom"],
            telephone=row["telephone"], email=row["email"],
            piece_identite=row["piece_identite"], nationalite=row["nationalite"],
            date_creation=row["date_creation"]
        )

    @classmethod
    def create(cls, nom, prenom, telephone, email, piece_identite, nationalite):
        db = DatabaseManager()
        cur = db.execute(
            """INSERT INTO clients (nom, prenom, telephone, email, piece_identite, nationalite)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nom, prenom, telephone, email, piece_identite, nationalite)
        )
        return cur.lastrowid

    @classmethod
    def update(cls, id, nom, prenom, telephone, email, piece_identite, nationalite):
        db = DatabaseManager()
        db.execute(
            """UPDATE clients
               SET nom=?, prenom=?, telephone=?, email=?, piece_identite=?, nationalite=?
               WHERE id=?""",
            (nom, prenom, telephone, email, piece_identite, nationalite, id)
        )

    @classmethod
    def delete(cls, id):
        db = DatabaseManager()
        db.execute("DELETE FROM clients WHERE id=?", (id,))

    @classmethod
    def get_by_id(cls, id):
        db = DatabaseManager()
        row = db.fetchone("SELECT * FROM clients WHERE id=?", (id,))
        return cls._from_row(row)

    @classmethod
    def get_all(cls, search_term=None):
        db = DatabaseManager()
        if search_term:
            like = f"%{search_term}%"
            rows = db.fetchall(
                """SELECT * FROM clients
                   WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ? OR email LIKE ?
                   ORDER BY nom""",
                (like, like, like, like)
            )
        else:
            rows = db.fetchall("SELECT * FROM clients ORDER BY nom")
        return [cls._from_row(r) for r in rows]

    @classmethod
    def get_historique(cls, client_id):
        """Retourne toutes les réservations passées et actuelles d'un client."""
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT r.*, c.numero AS chambre_numero, c.type AS chambre_type
               FROM reservations r
               JOIN chambres c ON r.chambre_id = c.id
               WHERE r.client_id = ?
               ORDER BY r.date_arrivee DESC""",
            (client_id,)
        )
        return rows

    @classmethod
    def has_reservations(cls, client_id):
        db = DatabaseManager()
        row = db.fetchone(
            "SELECT id FROM reservations WHERE client_id=? LIMIT 1", (client_id,)
        )
        return row is not None
