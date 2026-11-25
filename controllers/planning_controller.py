# FICHIER: planning_controller.py
"""
Contrôleur Planning : construit la grille chambres x jours pour le planning visuel.
"""

from datetime import datetime, timedelta

from models.reservation_model import Reservation
from models.chambre_model import Chambre


class PlanningController:

    @staticmethod
    def obtenir_grille(date_debut, nb_jours=14, type_filter=None, statut_filter=None):
        """
        Construit la grille du planning.
        Retourne :
            - jours : liste de nb_jours dates (str 'YYYY-MM-DD')
            - chambres : liste des objets Chambre (triées par numéro)
            - occupations : dict {chambre_id: {date_str: reservation_row}}
        """
        debut = datetime.strptime(date_debut, "%Y-%m-%d")
        jours = [(debut + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(nb_jours)]
        fin = (debut + timedelta(days=nb_jours)).strftime("%Y-%m-%d")

        chambres = Chambre.get_all(type_filter, statut_filter)
        reservations = Reservation.get_reservations_periode(date_debut, fin)

        occupations = {c.id: {} for c in chambres}

        for r in reservations:
            chambre_id = r["chambre_id"]
            if chambre_id not in occupations:
                continue

            arrivee = datetime.strptime(r["date_arrivee"], "%Y-%m-%d")
            depart = datetime.strptime(r["date_depart"], "%Y-%m-%d")

            for jour_str in jours:
                jour = datetime.strptime(jour_str, "%Y-%m-%d")
                if arrivee <= jour < depart:
                    occupations[chambre_id][jour_str] = r

        return {
            "jours": jours,
            "chambres": chambres,
            "occupations": occupations,
        }