"""
Contrôleur Facture : déclenche la génération PDF et l'enregistrement en base.
"""

from utils.pdf_generator import generer_facture_pdf
from models.facture_model import Facture
from models.reservation_model import Reservation


class FactureController:

    @staticmethod
    def generer(reservation_id):
        reservation = Reservation.get_by_id(reservation_id)
        if reservation is None:
            raise ValueError("Réservation introuvable.")
        filepath, numero = generer_facture_pdf(reservation_id)
        return filepath, numero

    @staticmethod
    def lister():
        return Facture.get_all()

    @staticmethod
    def obtenir_pour_reservation(reservation_id):
        return Facture.get_by_reservation(reservation_id)
