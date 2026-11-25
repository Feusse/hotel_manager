# FICHIER: dashboard_model.py
"""
Modèle Dashboard : requêtes d'agrégation en lecture seule pour les statistiques.
Ne modifie jamais les données, uniquement des SELECT.
"""

from datetime import datetime
from database.db_manager import DatabaseManager


class Dashboard:

    @staticmethod
    def taux_occupation():
        """Retourne (nb_occupees, nb_total, pourcentage)."""
        db = DatabaseManager()
        row = db.fetchone(
            """SELECT
                   COUNT(*) AS total,
                   SUM(CASE WHEN statut = 'Occupée' THEN 1 ELSE 0 END) AS occupees
               FROM chambres"""
        )
        total = row["total"] or 0
        occupees = row["occupees"] or 0
        pourcentage = round((occupees / total) * 100, 1) if total > 0 else 0.0
        return occupees, total, pourcentage

    @staticmethod
    def repartition_chambres_par_statut():
        """Retourne un dict {statut: nombre} pour toutes les chambres."""
        db = DatabaseManager()
        rows = db.fetchall(
            "SELECT statut, COUNT(*) AS nb FROM chambres GROUP BY statut"
        )
        return {r["statut"]: r["nb"] for r in rows}

    @staticmethod
    def revenus_mois_courant():
        """
        Revenus du mois en cours = somme des montants des réservations
        (hors annulées) dont la date d'arrivée est dans le mois courant,
        + somme des dépenses enregistrées ce mois-ci.
        """
        db = DatabaseManager()
        mois_courant = datetime.now().strftime("%Y-%m")

        row_reservations = db.fetchone(
            """SELECT COALESCE(SUM(montant_total), 0) AS total
               FROM reservations
               WHERE statut != 'Annulée'
                 AND strftime('%Y-%m', date_arrivee) = ?""",
            (mois_courant,)
        )
        row_depenses = db.fetchone(
            """SELECT COALESCE(SUM(d.montant), 0) AS total
               FROM depenses d
               JOIN reservations r ON d.reservation_id = r.id
               WHERE r.statut != 'Annulée'
                 AND strftime('%Y-%m', d.date_depense) = ?""",
            (mois_courant,)
        )
        total_sejours = row_reservations["total"] if row_reservations else 0.0
        total_depenses = row_depenses["total"] if row_depenses else 0.0
        return round(total_sejours, 2), round(total_depenses, 2), round(total_sejours + total_depenses, 2)

    @staticmethod
    def arrivees_aujourdhui():
        db = DatabaseManager()
        today = datetime.now().strftime("%Y-%m-%d")
        rows = db.fetchall(
            """SELECT r.*, cl.nom AS client_nom, cl.prenom AS client_prenom,
                      ch.numero AS chambre_numero
               FROM reservations r
               JOIN clients cl ON r.client_id = cl.id
               JOIN chambres ch ON r.chambre_id = ch.id
               WHERE r.date_arrivee = ? AND r.statut = 'Confirmée'
               ORDER BY cl.nom""",
            (today,)
        )
        return rows

    @staticmethod
    def departs_aujourdhui():
        db = DatabaseManager()
        today = datetime.now().strftime("%Y-%m-%d")
        rows = db.fetchall(
            """SELECT r.*, cl.nom AS client_nom, cl.prenom AS client_prenom,
                      ch.numero AS chambre_numero
               FROM reservations r
               JOIN clients cl ON r.client_id = cl.id
               JOIN chambres ch ON r.chambre_id = ch.id
               WHERE r.date_depart = ? AND r.statut = 'Confirmée'
               ORDER BY cl.nom""",
            (today,)
        )
        return rows

    @staticmethod
    def reservations_actives_count():
        db = DatabaseManager()
        row = db.fetchone(
            "SELECT COUNT(*) AS nb FROM reservations WHERE statut = 'Confirmée'"
        )
        return row["nb"] if row else 0

    @staticmethod
    def top_clients(limit=5):
        """
        Classement des clients par montant total dépensé (séjours + dépenses),
        toutes réservations non-annulées confondues.
        """
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT
                   cl.id, cl.nom, cl.prenom,
                   COALESCE(SUM(r.montant_total), 0) AS total_sejours,
                   COALESCE((
                       SELECT SUM(d.montant) FROM depenses d
                       JOIN reservations r2 ON d.reservation_id = r2.id
                       WHERE r2.client_id = cl.id AND r2.statut != 'Annulée'
                   ), 0) AS total_depenses,
                   COUNT(r.id) AS nb_sejours
               FROM clients cl
               LEFT JOIN reservations r ON r.client_id = cl.id AND r.statut != 'Annulée'
               GROUP BY cl.id
               HAVING nb_sejours > 0
               ORDER BY (total_sejours + total_depenses) DESC
               LIMIT ?""",
            (limit,)
        )
        return rows

    @staticmethod
    def repartition_par_type_chambre():
        """Retourne un dict {type: {'total': n, 'occupees': n}} pour le graphique."""
        db = DatabaseManager()
        rows = db.fetchall(
            """SELECT type,
                      COUNT(*) AS total,
                      SUM(CASE WHEN statut = 'Occupée' THEN 1 ELSE 0 END) AS occupees
               FROM chambres
               GROUP BY type"""
        )
        return {r["type"]: {"total": r["total"], "occupees": r["occupees"]} for r in rows}
        
        