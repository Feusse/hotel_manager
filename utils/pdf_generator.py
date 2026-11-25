# FICHIER: pdf_generator.py
"""
Génération de factures PDF avec ReportLab.
Design simple, professionnel, en A4.
Inclut désormais le détail du séjour ET les dépenses annexes du client,
avec un montant total consolidé (séjour + dépenses).
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

from models.facture_model import Facture
from models.reservation_model import Reservation
from models.depense_model import Depense

INVOICES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "invoices"
)
os.makedirs(INVOICES_DIR, exist_ok=True)

HOTEL_NAME = "KRYSTAL PALACE Hôtel"
HOTEL_ADDRESS = "AKWA NORD, Douala, Cameroun"
HOTEL_CONTACT = "Tél: +237  622 00 00 00   |  contact@krystalPalace-hotel.com"


def generer_facture_pdf(reservation_id):
    """
    Génère un PDF de facture pour une réservation donnée.
    Inclut le séjour + les dépenses annexes, avec un total consolidé.
    Retourne (chemin_pdf, numero_facture).
    """
    data = Reservation.get_details_completes(reservation_id)
    if data is None:
        raise ValueError("Réservation introuvable pour génération de facture.")

    depenses = Depense.get_by_reservation(reservation_id)
    total_depenses = sum(d.montant for d in depenses)
    montant_sejour = data["montant_total"]
    montant_final = round(montant_sejour + total_depenses, 2)

    numero_facture = Facture.generer_numero()
    filename = f"{numero_facture}.pdf"
    filepath = os.path.join(INVOICES_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=2,
        textColor=colors.HexColor("#1a3c5e")
    )
    normal = styles["Normal"]
    right_style = ParagraphStyle("RightAlign", parent=normal, alignment=TA_RIGHT)
    center_style = ParagraphStyle("CenterAlign", parent=normal, alignment=TA_CENTER)
    small_gray = ParagraphStyle(
        "SmallGray", parent=normal, fontSize=9, textColor=colors.HexColor("#666666")
    )
    section_title = ParagraphStyle(
        "SectionTitle", parent=styles["Heading3"], fontSize=12, spaceBefore=4, spaceAfter=4,
        textColor=colors.HexColor("#1a3c5e")
    )

    elements = []

    # --- En-tête ---
    elements.append(Paragraph(HOTEL_NAME, title_style))
    elements.append(Paragraph(HOTEL_ADDRESS, small_gray))
    elements.append(Paragraph(HOTEL_CONTACT, small_gray))
    elements.append(Spacer(1, 10 * mm))

    elements.append(Paragraph(f"<b>FACTURE N° {numero_facture}</b>", styles["Heading2"]))
    elements.append(Paragraph(
        f"Date d'émission : {datetime.now().strftime('%d/%m/%Y')}", normal
    ))
    elements.append(Spacer(1, 8 * mm))

    # --- Informations client ---
    client_info = [
        ["Client", f"{data['client_prenom']} {data['client_nom']}"],
        ["Téléphone", data["client_telephone"] or "-"],
        ["Email", data["client_email"] or "-"],
        ["Pièce d'identité", data["client_piece"] or "-"],
        ["Nationalité", data["client_nationalite"] or "-"],
    ]
    client_table = Table(client_info, colWidths=[45 * mm, 110 * mm])
    client_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1a3c5e")),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 8 * mm))

    # --- Détails du séjour ---
    nb_nuits = data["nb_nuits"]
    prix_nuit = data["chambre_prix"]

    elements.append(Paragraph("Séjour", section_title))
    table_data = [
        ["Description", "Détails"],
        ["Chambre", f"N° {data['chambre_numero']} ({data['chambre_type']})"],
        ["Date d'arrivée", data["date_arrivee"]],
        ["Date de départ", data["date_depart"]],
        ["Nombre de nuits", str(nb_nuits)],
        ["Prix par nuit", f"{prix_nuit:.2f} XAF"],
    ]
    detail_table = Table(table_data, colWidths=[70 * mm, 85 * mm])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c5e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
    ]))
    elements.append(detail_table)

    sous_total_sejour = [["Sous-total séjour", f"{montant_sejour:.2f} XAF"]]
    sous_total_table = Table(sous_total_sejour, colWidths=[70 * mm, 85 * mm])
    sous_total_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.HexColor("#cccccc")),
    ]))
    elements.append(sous_total_table)
    elements.append(Spacer(1, 8 * mm))

    # --- Dépenses annexes (uniquement si présentes) ---
    if depenses:
        elements.append(Paragraph("Dépenses durant le séjour", section_title))
        depenses_data = [["Description", "Date", "Montant"]]
        for d in depenses:
            date_affichee = d.date_depense.split(" ")[0] if d.date_depense else "-"
            depenses_data.append([d.description, date_affichee, f"{d.montant:.2f} XAF"])

        depenses_table = Table(depenses_data, colWidths=[85 * mm, 35 * mm, 35 * mm])
        depenses_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c5e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
        ]))
        elements.append(depenses_table)

        sous_total_depenses = [["Sous-total dépenses", f"{total_depenses:.2f} XAF"]]
        sous_total_dep_table = Table(sous_total_depenses, colWidths=[85 * mm, 35 * mm])
        sous_total_dep_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.HexColor("#cccccc")),
        ]))
        elements.append(sous_total_dep_table)
        elements.append(Spacer(1, 8 * mm))

    # --- Total consolidé ---
    total_data = [["MONTANT TOTAL (séjour + dépenses)", f"{montant_final:.2f} XAF"]]
    total_table = Table(total_data, colWidths=[110 * mm, 45 * mm])
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8b923")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a3c5e")),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 15 * mm))

    elements.append(Paragraph(
        "Merci de votre confiance. Nous espérons vous revoir bientôt.",
        center_style
    ))

    doc.build(elements)

    # Enregistrement en base : le montant total de la facture inclut désormais les dépenses
    Facture.create(reservation_id, montant_final, filepath)

    return filepath, numero_facture