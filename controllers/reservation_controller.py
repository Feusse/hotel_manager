"""
Contrôleur Réservation : orchestre la vérification de disponibilité,
le calcul du montant, et les actions d'annulation / clôture.
"""

from models.reservation_model import Reservation
from models.chambre_model import Chambre
from models.client_model import Client
from utils.validators import valider_date


class ReservationController:

    @staticmethod
    def lister(statut_filter=None):
        return Reservation.get_all(statut_filter)

    @staticmethod
    def calculer_apercu(chambre_id, date_arrivee, date_depart):
        """
        Calcule un aperçu (nuits + montant) SANS créer la réservation.
        Utilisé pour l'affichage en temps réel dans le formulaire.
        Lève ValueError si dates invalides ou chambre indisponible.
        """
        if not valider_date(date_arrivee) or not valider_date(date_depart):
            raise ValueError("Format de date invalide (attendu AAAA-MM-JJ).")

        nb_nuits = Reservation.calculer_nuits(date_arrivee, date_depart)
        if nb_nuits <= 0:
            raise ValueError("La date de départ doit être postérieure à la date d'arrivée.")

        chambre = Chambre.get_by_id(chambre_id)
        if chambre is None:
            raise ValueError("Chambre introuvable.")

        disponible = Reservation.chambre_disponible(chambre_id, date_arrivee, date_depart)
        montant = round(nb_nuits * chambre.prix_nuit, 2)

        return {
            "nb_nuits": nb_nuits,
            "montant_total": montant,
            "disponible": disponible,
            "prix_nuit": chambre.prix_nuit
        }

    @staticmethod
    def creer_reservation(client_id, chambre_id, date_arrivee, date_depart):
        if not client_id:
            raise ValueError("Veuillez sélectionner un client.")
        if not chambre_id:
            raise ValueError("Veuillez sélectionner une chambre.")
        if not valider_date(date_arrivee) or not valider_date(date_depart):
            raise ValueError("Format de date invalide (attendu AAAA-MM-JJ).")

        chambre = Chambre.get_by_id(chambre_id)
        if chambre is None:
            raise ValueError("Chambre introuvable.")

        client = Client.get_by_id(client_id)
        if client is None:
            raise ValueError("Client introuvable.")

        # La vérification de disponibilité + calcul est faite dans le modèle (create)
        reservation_id, nb_nuits, montant_total = Reservation.create(
            client_id, chambre_id, date_arrivee, date_depart, chambre.prix_nuit
        )
        return reservation_id, nb_nuits, montant_total

    @staticmethod
    def annuler_reservation(reservation_id):
        Reservation.annuler(reservation_id)

    @staticmethod
    def terminer_sejour(reservation_id):
        Reservation.terminer(reservation_id)

    @staticmethod
    def dates_occupees(chambre_id):
        return Reservation.get_dates_occupees(chambre_id)
