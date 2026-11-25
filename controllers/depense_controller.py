# FICHIER: depense_controller.py
"""
Contrôleur Dépense : validation + orchestration entre l'UI et le modèle.
"""

from models.depense_model import Depense
from models.reservation_model import Reservation
from utils.validators import champs_obligatoires_remplis, valider_prix


class DepenseController:

    @staticmethod
    def lister(reservation_id):
        return Depense.get_by_reservation(reservation_id)

    @staticmethod
    def total(reservation_id):
        return Depense.get_total_by_reservation(reservation_id)

    @staticmethod
    def ajouter(reservation_id, description, montant):
        if not champs_obligatoires_remplis(description, montant):
            raise ValueError("La description et le montant sont obligatoires.")
        if not valider_prix(montant):
            raise ValueError("Le montant doit être un nombre positif.")

        reservation = Reservation.get_by_id(reservation_id)
        if reservation is None:
            raise ValueError("Réservation introuvable.")
        if reservation.statut == "Annulée":
            raise ValueError("Impossible d'ajouter une dépense à une réservation annulée.")

        return Depense.create(reservation_id, description.strip(), float(montant))

    @staticmethod
    def supprimer(depense_id):
        Depense.delete(depense_id)
        