"""
Modèle Réservation : cœur métier de l'application.
Gère la vérification de disponibilité (anti-chevauchement de dates)
et le calcul automatique du montant total.
"""

from datetime import datetime
from database.db_manager import DatabaseManager


class Reservation:
    def __init__(self, id=None, client_id=None, chambre_id=None,
                 date_arrivee=None, date_depart=None, nb_nuits=0,
                 montant_total=0.0, statut="Confirmée", date_creation=None):
        self.id = id
        self.client_id = client_id
        self.chambre_id = chambre_id
        self.date_arrivee = date_arrivee
        self.date_depart = date_depart
        self.nb_nuits = nb_nuits
        self.montant_total = montant_total
        self.statut = statut
        self.date_creation = date_creation

    @staticmethod
    def _from_row(row):
        if row is None:
            return None
        return Reservation(
            id=row["id"], client_id=row["client_id"], chambre_id=row["chambre_id"],
            date_arrivee=row["date_arrivee"], date_depart=row["date_depart"],
            nb_nuits=row["nb_nuits"], montant_total=row["montant_total"],
            statut=row["statut"], date_creation=row["date_creation"]
        )

    # ---------- Utilitaires de dates ----------

    @staticmethod
    def parse_date(date_str):
        """Accepte 'YYYY-MM-DD'."""
        return datetime.strptime(date_str, "%Y-%m-%d")

    @classmethod
    def calculer_nuits(cls, date_arrivee, date_depart):
        d1 = cls.parse_date(date_arrivee)
        d2 = cls.parse_date(date_depart)
        delta = (d2 - d1).days
        return delta

    # ---------- Vérification de disponibilité ----------

    @classmethod
    def chambre_disponible(cls, chambre_id, date_arrivee, date_depart, exclude_reservation_id=None):
        """
        Vérifie qu'aucune réservation active (Confirmée) pour cette chambre
        ne chevauche l'intervalle [date_arrivee, date_depart).
        Chevauchement classique : (start1 < end2) AND (start2 < end1)
        """
        db = DatabaseManager()
        query = """
            SELECT id FROM reservations
            WHERE chambre_id = ?
              AND statut = 'Confirmée'
              AND date_arrivee < ?
              AND date_depart > ?
        """
        params = [chambre_id, date_depart, date_arrivee]

        if exclude_reservation_id:
            query += " AND id != ?"
            params.append(exclude_reservation_id)

        row = db.fetchone(query, tuple(params))
        return row is None  # True = disponible

    @classmethod
    def get_dates_occupees(cls, chambre_id):
        """Retourne la liste des périodes déjà réservées pour une chambre donnée."""
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT date_arrivee, date_depart FROM reservations
               WHERE chambre_id=? AND statut='Confirmée'
               ORDER BY date_arrivee""",
            (chambre_id,)
        )
        return [(r["date_arrivee"], r["date_depart"]) for r in rows]
    
    @classmethod
    def get_reservations_periode(cls, date_debut, date_fin):
        """
        Retourne toutes les réservations actives (Confirmée) de toutes les chambres
        qui chevauchent la plage [date_debut, date_fin). Utilisé par le planning visuel.
        """
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT r.*, cl.nom AS client_nom, cl.prenom AS client_prenom,
                      ch.numero AS chambre_numero
               FROM reservations r
               JOIN clients cl ON r.client_id = cl.id
               JOIN chambres ch ON r.chambre_id = ch.id
               WHERE r.statut = 'Confirmée'
                 AND r.date_arrivee < ?
                 AND r.date_depart > ?
               ORDER BY ch.numero, r.date_arrivee""",
            (date_fin, date_debut)
        )
        return rows

    # ---------- CRUD ----------

    @classmethod
    def create(cls, client_id, chambre_id, date_arrivee, date_depart, prix_nuit):
        """
        Crée une réservation après validation complète :
        - dates cohérentes (arrivée < départ)
        - chambre disponible sur la période
        Lève une ValueError explicite sinon (à afficher dans l'UI).
        """
        d1 = cls.parse_date(date_arrivee)
        d2 = cls.parse_date(date_depart)

        if d2 <= d1:
            raise ValueError("La date de départ doit être postérieure à la date d'arrivée.")

        if not cls.chambre_disponible(chambre_id, date_arrivee, date_depart):
            raise ValueError("Cette chambre est déjà réservée sur la période sélectionnée.")

        nb_nuits = cls.calculer_nuits(date_arrivee, date_depart)
        montant_total = round(nb_nuits * prix_nuit, 2)

        db = DatabaseManager()
        cur = db.execute(
            """INSERT INTO reservations
               (client_id, chambre_id, date_arrivee, date_depart, nb_nuits, montant_total, statut)
               VALUES (?, ?, ?, ?, ?, ?, 'Confirmée')""",
            (client_id, chambre_id, date_arrivee, date_depart, nb_nuits, montant_total)
        )
        reservation_id = cur.lastrowid

        # La chambre passe automatiquement en "Occupée"
        db.execute("UPDATE chambres SET statut='Occupée' WHERE id=?", (chambre_id,))

        return reservation_id, nb_nuits, montant_total

    @classmethod
    def annuler(cls, reservation_id):
        db = DatabaseManager()
        res = cls.get_by_id(reservation_id)
        if res is None:
            raise ValueError("Réservation introuvable.")

        db.execute("UPDATE reservations SET statut='Annulée' WHERE id=?", (reservation_id,))

        # Si la chambre n'a plus aucune réservation confirmée active aujourd'hui, la libérer
        still_booked = db.fetchone(
            """SELECT id FROM reservations
               WHERE chambre_id=? AND statut='Confirmée' LIMIT 1""",
            (res.chambre_id,)
        )
        if still_booked is None:
            db.execute("UPDATE chambres SET statut='Disponible' WHERE id=?", (res.chambre_id,))

    @classmethod
    def terminer(cls, reservation_id):
        """Marque une réservation comme terminée (check-out) et libère la chambre."""
        db = DatabaseManager()
        res = cls.get_by_id(reservation_id)
        if res is None:
            raise ValueError("Réservation introuvable.")
        db.execute("UPDATE reservations SET statut='Terminée' WHERE id=?", (reservation_id,))
        db.execute("UPDATE chambres SET statut='Disponible' WHERE id=?", (res.chambre_id,))

    @classmethod
    def get_by_id(cls, id):
        db = DatabaseManager()
        row = db.fetchone("SELECT * FROM reservations WHERE id=?", (id,))
        return cls._from_row(row)

    @classmethod
    def get_all(cls, statut_filter=None):
        db = DatabaseManager()
        query = """
            SELECT r.*, cl.nom AS client_nom, cl.prenom AS client_prenom,
                   ch.numero AS chambre_numero, ch.type AS chambre_type
            FROM reservations r
            JOIN clients cl ON r.client_id = cl.id
            JOIN chambres ch ON r.chambre_id = ch.id
            WHERE 1=1
        """
        params = []
        if statut_filter and statut_filter != "Toutes":
            query += " AND r.statut = ?"
            params.append(statut_filter)
        query += " ORDER BY r.date_arrivee DESC"
        return db.fetchall(query, tuple(params))

    @classmethod
    def get_details_completes(cls, reservation_id):
        """Utilisé pour la génération de facture : jointure complète."""
        db = DatabaseManager()
        row = db.fetchone(
            """SELECT r.*, 
                      cl.nom AS client_nom, cl.prenom AS client_prenom,
                      cl.telephone AS client_telephone, cl.email AS client_email,
                      cl.piece_identite AS client_piece, cl.nationalite AS client_nationalite,
                      ch.numero AS chambre_numero, ch.type AS chambre_type,
                      ch.prix_nuit AS chambre_prix
               FROM reservations r
               JOIN clients cl ON r.client_id = cl.id
               JOIN chambres ch ON r.chambre_id = ch.id
               WHERE r.id = ?""",
            (reservation_id,)
        )
        return row
