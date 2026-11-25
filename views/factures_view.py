# FICHIER: factures_view.py
"""
Vue : Consultation des factures générées.
"""

import customtkinter as ctk
from tkinter import messagebox
import os
import subprocess
import sys

from controllers.facture_controller import FactureController
from utils.printer import imprimer_pdf, ImpressionError


class FacturesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build_layout()
        self.refresh_liste()

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Factures générées",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=(0, 15)
        )

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _ouvrir_pdf(self, chemin):
        if not chemin or not os.path.exists(chemin):
            messagebox.showerror("Erreur", "Le fichier PDF est introuvable.")
            return
        try:
            if sys.platform == "win32":
                os.startfile(chemin)
            elif sys.platform == "darwin":
                subprocess.call(["open", chemin])
            else:
                subprocess.call(["xdg-open", chemin])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le PDF : {e}")

    def _imprimer_pdf(self, chemin):
        try:
            imprimer_pdf(chemin)
            messagebox.showinfo("Impression", "La facture a été envoyée à l'imprimante.")
        except ImpressionError as e:
            messagebox.showerror("Erreur d'impression", str(e))

    def refresh_liste(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        factures = FactureController.lister()

        if not factures:
            ctk.CTkLabel(self.scroll_frame, text="Aucune facture générée pour le moment.",
                         text_color="gray").pack(pady=20)
            return

        for f in factures:
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color=("gray92", "gray17"))
            card.pack(fill="x", pady=5, padx=5)
            card.grid_columnconfigure(0, weight=1)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=0, sticky="ew", padx=15, pady=12)
            ctk.CTkLabel(
                info, text=f"{f['numero_facture']}  —  {f['client_prenom']} {f['client_nom']}",
                font=ctk.CTkFont(size=13, weight="bold"), anchor="w"
            ).pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=f"Séjour du {f['date_arrivee']} au {f['date_depart']}  •  "
                     f"{f['montant_total']:.2f} XAF  •  Émise le {f['date_emission']}",
                text_color="gray", anchor="w"
            ).pack(anchor="w")

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=15, pady=12)

            ctk.CTkButton(
                btn_frame, text="Ouvrir le PDF", width=110, height=28,
                fg_color="#1f6aa5",
                command=lambda c=f["chemin_pdf"]: self._ouvrir_pdf(c)
            ).pack(side="left", padx=(0, 6))

            ctk.CTkButton(
                btn_frame, text="Imprimer", width=90, height=28,
                fg_color="#2a5d34", hover_color="#347040",
                command=lambda c=f["chemin_pdf"]: self._imprimer_pdf(c)
            ).pack(side="left")
            