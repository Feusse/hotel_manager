 # FICHIER: printer.py
"""
Utilitaire d'impression de fichiers PDF vers l'imprimante par défaut du système.

Sous Windows : utilise os.startfile(chemin, "print"), qui délègue l'impression
au lecteur PDF associé (Edge, Adobe Reader, etc.).
Sous macOS/Linux : utilise la commande `lp` (CUPS).
"""

import os
import sys
import subprocess


class ImpressionError(Exception):
    """Levée quand l'impression échoue, avec un message adapté à afficher à l'utilisateur."""
    pass


def imprimer_pdf(chemin_pdf):
    """
    Envoie le PDF à l'imprimante par défaut du système.
    Lève ImpressionError avec un message clair en cas d'échec.
    """
    if not chemin_pdf or not os.path.exists(chemin_pdf):
        raise ImpressionError("Le fichier PDF de la facture est introuvable.")

    try:
        if sys.platform == "win32":
            os.startfile(chemin_pdf, "print")
        elif sys.platform == "darwin":
            subprocess.run(["lp", chemin_pdf], check=True)
        else:
            subprocess.run(["lp", chemin_pdf], check=True)
    except FileNotFoundError:
        raise ImpressionError(
            "Aucune imprimante par défaut n'a été trouvée, ou aucun lecteur PDF "
            "n'est associé aux fichiers .pdf sur cet ordinateur."
        )
    except subprocess.CalledProcessError:
        raise ImpressionError(
            "L'impression a échoué. Vérifiez qu'une imprimante est bien connectée "
            "et configurée comme imprimante par défaut."
        )
    except OSError as e:
        raise ImpressionError(f"Impossible de lancer l'impression : {e}")