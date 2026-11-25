"""
Validations réutilisables entre les différentes vues.
"""

import re
from datetime import datetime


def valider_email(email):
    if not email:
        return True  # champ optionnel
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def valider_telephone(tel):
    if not tel:
        return True
    pattern = r"^[\d\s\+\-\(\)]{6,20}$"
    return re.match(pattern, tel) is not None


def valider_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def valider_prix(prix_str):
    try:
        prix = float(prix_str)
        return prix > 0
    except (ValueError, TypeError):
        return False


def champs_obligatoires_remplis(*valeurs):
    return all(v is not None and str(v).strip() != "" for v in valeurs)
