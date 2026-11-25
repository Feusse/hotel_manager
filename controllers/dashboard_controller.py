# FICHIER: dashboard_controller.py
"""
Contrôleur Dashboard : agrège toutes les statistiques nécessaires
à la vue en un seul point d'entrée simple pour l'UI.
"""

from models.dashboard_model import Dashboard


class DashboardController:

    @staticmethod
    def obtenir_statistiques():
        occupees, total_chambres, taux = Dashboard.taux_occupation()
        sejours, depenses, total_revenus = Dashboard.revenus_mois_courant()

        return {
            "occupation": {
                "occupees": occupees,
                "total": total_chambres,
                "pourcentage": taux,
            },
            "revenus_mois": {
                "sejours": sejours,
                "depenses": depenses,
                "total": total_revenus,
            },
            "reservations_actives": Dashboard.reservations_actives_count(),
            "arrivees_aujourdhui": Dashboard.arrivees_aujourdhui(),
            "departs_aujourdhui": Dashboard.departs_aujourdhui(),
            "top_clients": Dashboard.top_clients(limit=5),
            "repartition_types": Dashboard.repartition_par_type_chambre(),
            "repartition_statuts": Dashboard.repartition_chambres_par_statut(),
        }