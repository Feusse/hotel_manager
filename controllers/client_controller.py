"""
Contrôleur Client.
"""

from models.client_model import Client
from utils.validators import (
    champs_obligatoires_remplis, valider_email, valider_telephone
)


class ClientController:

    @staticmethod
    def lister(search_term=None):
        return Client.get_all(search_term)

    @staticmethod
    def obtenir(client_id):
        return Client.get_by_id(client_id)

    @staticmethod
    def ajouter(nom, prenom, telephone, email, piece_identite, nationalite):
        if not champs_obligatoires_remplis(nom, prenom):
            raise ValueError("Le nom et le prénom sont obligatoires.")
        if not valider_email(email):
            raise ValueError("L'adresse email n'est pas valide.")
        if not valider_telephone(telephone):
            raise ValueError("Le numéro de téléphone n'est pas valide.")

        return Client.create(
            nom.strip(), prenom.strip(), telephone.strip() if telephone else "",
            email.strip() if email else "", piece_identite.strip() if piece_identite else "",
            nationalite.strip() if nationalite else ""
        )

    @staticmethod
    def modifier(client_id, nom, prenom, telephone, email, piece_identite, nationalite):
        if not champs_obligatoires_remplis(nom, prenom):
            raise ValueError("Le nom et le prénom sont obligatoires.")
        if not valider_email(email):
            raise ValueError("L'adresse email n'est pas valide.")
        if not valider_telephone(telephone):
            raise ValueError("Le numéro de téléphone n'est pas valide.")

        Client.update(
            client_id, nom.strip(), prenom.strip(),
            telephone.strip() if telephone else "", email.strip() if email else "",
            piece_identite.strip() if piece_identite else "",
            nationalite.strip() if nationalite else ""
        )

    @staticmethod
    def supprimer(client_id):
        Client.delete(client_id)

    @staticmethod
    def historique(client_id):
        return Client.get_historique(client_id)
