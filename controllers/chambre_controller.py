"""
Contrôleur Chambre : orchestre les validations et appelle le modèle.
La vue ne parle jamais directement au modèle, toujours via ce contrôleur.
"""

from models.chambre_model import Chambre
from utils.validators import champs_obligatoires_remplis, valider_prix

TYPES_CHAMBRE = ["Simple", "Double", "Suite", "VIP"]
STATUTS_CHAMBRE = ["Disponible", "Occupée", "Maintenance"]


class ChambreController:

    @staticmethod
    def lister(type_filter=None, statut_filter=None):
        return Chambre.get_all(type_filter, statut_filter)

    @staticmethod
    def obtenir(chambre_id):
        return Chambre.get_by_id(chambre_id)

    @staticmethod
    def ajouter(numero, type_, prix_nuit, statut, description, photo_path=None):
        if not champs_obligatoires_remplis(numero, type_, prix_nuit):
            raise ValueError("Le numéro, le type et le prix sont obligatoires.")
        if not valider_prix(prix_nuit):
            raise ValueError("Le prix doit être un nombre positif.")
        if Chambre.numero_exists(numero):
            raise ValueError(f"Une chambre avec le numéro '{numero}' existe déjà.")

        return Chambre.create(
            numero.strip(), type_, float(prix_nuit), statut,
            description.strip() if description else "", photo_path
        )

    @staticmethod
    def modifier(chambre_id, numero, type_, prix_nuit, statut, description, photo_path=None):
        if not champs_obligatoires_remplis(numero, type_, prix_nuit):
            raise ValueError("Le numéro, le type et le prix sont obligatoires.")
        if not valider_prix(prix_nuit):
            raise ValueError("Le prix doit être un nombre positif.")
        if Chambre.numero_exists(numero, exclude_id=chambre_id):
            raise ValueError(f"Une chambre avec le numéro '{numero}' existe déjà.")

        Chambre.update(
            chambre_id, numero.strip(), type_, float(prix_nuit), statut,
            description.strip() if description else "", photo_path
        )

    @staticmethod
    def supprimer(chambre_id):
        Chambre.delete(chambre_id)
