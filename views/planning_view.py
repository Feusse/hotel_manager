# FICHIER: planning_view.py
"""
Vue : Planning visuel des chambres.
Grille chambres (lignes) x jours (colonnes), avec navigation temporelle
et clic sur un créneau libre pour pré-remplir une réservation.
"""

import customtkinter as ctk
from datetime import datetime, timedelta

from controllers.planning_controller import PlanningController
from controllers.chambre_controller import ChambreController, TYPES_CHAMBRE

NB_JOURS_AFFICHES = 14
LARGEUR_COLONNE_CHAMBRE = 130
LARGEUR_COLONNE_JOUR = 70

COULEUR_LIBRE = ("gray95", "gray22")
COULEUR_OCCUPEE = "#3a6ea5"
COULEUR_AUJOURDHUI_BORDURE = "#e8b923"

JOURS_SEMAINE_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
MOIS_FR = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]


class PlanningView(ctk.CTkFrame):
    def __init__(self, master, on_creneau_libre=None):
        """
        on_creneau_libre : callback(chambre_id, date_str) appelé quand l'utilisateur
        clique sur un créneau libre, pour permettre à la fenêtre principale de
        basculer vers l'onglet Réservations pré-rempli.
        """
        super().__init__(master, fg_color="transparent")
        self.on_creneau_libre = on_creneau_libre
        self.date_debut = datetime.now()
        self._build_layout()
        self.refresh()

    # ---------------------------------------------------------------
    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Barre supérieure : navigation + filtres ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkButton(
            header, text="◀ Précédent", width=110, command=self._periode_precedente,
            fg_color="#3b3b3b", hover_color="#4d4d4d"
        ).pack(side="left")

        self.label_periode = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=15, weight="bold")
        )
        self.label_periode.pack(side="left", padx=15)

        ctk.CTkButton(
            header, text="Suivant ▶", width=110, command=self._periode_suivante,
            fg_color="#3b3b3b", hover_color="#4d4d4d"
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Aujourd'hui", width=100, command=self._aller_aujourdhui,
            fg_color="#1f6aa5"
        ).pack(side="left", padx=(15, 0))

        ctk.CTkLabel(header, text="Type :").pack(side="left", padx=(25, 5))
        self.filter_type = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(
            header, values=["Tous"] + TYPES_CHAMBRE, variable=self.filter_type,
            command=lambda _: self.refresh(), width=110
        ).pack(side="left")

        legende = ctk.CTkFrame(header, fg_color="transparent")
        legende.pack(side="right")
        self._legende_item(legende, COULEUR_LIBRE[1], "Libre")
        self._legende_item(legende, COULEUR_OCCUPEE, "Occupée")

        # --- Zone grille scrollable ---
        self.grille_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grille_scroll.grid(row=1, column=0, sticky="nsew")

    def _legende_item(self, parent, couleur, texte):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=8)
        ctk.CTkLabel(frame, text="  ", fg_color=couleur, width=16, height=16, corner_radius=3).pack(side="left")
        ctk.CTkLabel(frame, text=texte, text_color="gray").pack(side="left", padx=(4, 0))

    # ---------------------------------------------------------------
    def _periode_precedente(self):
        self.date_debut -= timedelta(days=NB_JOURS_AFFICHES)
        self.refresh()

    def _periode_suivante(self):
        self.date_debut += timedelta(days=NB_JOURS_AFFICHES)
        self.refresh()

    def _aller_aujourdhui(self):
        self.date_debut = datetime.now()
        self.refresh()

    def _formater_jour_court(self, date_str):
        d = datetime.strptime(date_str, "%Y-%m-%d")
        jour_semaine = JOURS_SEMAINE_FR[d.weekday()]
        return f"{jour_semaine}\n{d.day}"

    def _formater_periode(self, jours):
        d1 = datetime.strptime(jours[0], "%Y-%m-%d")
        d2 = datetime.strptime(jours[-1], "%Y-%m-%d")
        if d1.month == d2.month:
            return f"{d1.day} - {d2.day} {MOIS_FR[d1.month - 1]} {d1.year}"
        return f"{d1.day} {MOIS_FR[d1.month - 1]} - {d2.day} {MOIS_FR[d2.month - 1]} {d2.year}"

    # ---------------------------------------------------------------
    def _on_creneau_click(self, chambre_id, date_str, occupee, reservation_info=None):
        if occupee:
            return
        if self.on_creneau_libre:
            self.on_creneau_libre(chambre_id, date_str)

    def _construire_cellule(self, parent, chambre_id, date_str, reservation, est_aujourdhui, row, col):
        occupee = reservation is not None

        if occupee:
            cell = ctk.CTkFrame(
                parent, width=LARGEUR_COLONNE_JOUR, height=44, corner_radius=6,
                fg_color=COULEUR_OCCUPEE, cursor="hand2"
            )
        else:
            cell = ctk.CTkFrame(
                parent, width=LARGEUR_COLONNE_JOUR, height=44, corner_radius=6,
                fg_color=COULEUR_LIBRE, cursor="hand2"
            )

        if est_aujourdhui:
            cell.configure(border_width=2, border_color=COULEUR_AUJOURDHUI_BORDURE)

        cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        cell.grid_propagate(False)

        if occupee:
            texte = f"{reservation['client_prenom'][:1]}. {reservation['client_nom']}"
            label = ctk.CTkLabel(cell, text=texte, text_color="white", font=ctk.CTkFont(size=10), wraplength=LARGEUR_COLONNE_JOUR - 10)
            label.place(relx=0.5, rely=0.5, anchor="center")
            tooltip_text = (
                f"{reservation['client_prenom']} {reservation['client_nom']}\n"
                f"Du {reservation['date_arrivee']} au {reservation['date_depart']}"
            )
            self._bind_tooltip(cell, tooltip_text)
            self._bind_tooltip(label, tooltip_text)
        else:
            cell.bind("<Button-1>", lambda e: self._on_creneau_click(chambre_id, date_str, False))

    def _bind_tooltip(self, widget, text):
        """Tooltip simple : affiche un petit label flottant au survol."""
        tooltip_window = {"win": None}

        def on_enter(event):
            win = ctk.CTkToplevel(self)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            x = event.x_root + 12
            y = event.y_root + 12
            win.geometry(f"+{x}+{y}")
            label = ctk.CTkLabel(
                win, text=text, fg_color=("gray20", "gray20"), text_color="white",
                corner_radius=6, padx=10, pady=6, justify="left"
            )
            label.pack()
            tooltip_window["win"] = win

        def on_leave(event):
            if tooltip_window["win"] is not None:
                tooltip_window["win"].destroy()
                tooltip_window["win"] = None

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # ---------------------------------------------------------------
    def refresh(self):
        for widget in self.grille_scroll.winfo_children():
            widget.destroy()

        date_debut_str = self.date_debut.strftime("%Y-%m-%d")
        grille = PlanningController.obtenir_grille(
            date_debut_str, nb_jours=NB_JOURS_AFFICHES, type_filter=self.filter_type.get()
        )
        jours = grille["jours"]
        chambres = grille["chambres"]
        occupations = grille["occupations"]

        self.label_periode.configure(text=self._formater_periode(jours))

        today_str = datetime.now().strftime("%Y-%m-%d")

        if not chambres:
            ctk.CTkLabel(self.grille_scroll, text="Aucune chambre pour ce filtre.",
                         text_color="gray").pack(pady=30)
            return

        header_row = ctk.CTkFrame(self.grille_scroll, fg_color="transparent")
        header_row.pack(anchor="w")

        ctk.CTkLabel(
            header_row, text="Chambre", width=LARGEUR_COLONNE_CHAMBRE, height=44,
            font=ctk.CTkFont(weight="bold"), anchor="w"
        ).grid(row=0, column=0, padx=2, pady=2, sticky="w")

        for col, jour in enumerate(jours, start=1):
            est_aujourdhui = jour == today_str
            couleur_texte = COULEUR_AUJOURDHUI_BORDURE if est_aujourdhui else None
            lbl = ctk.CTkLabel(
                header_row, text=self._formater_jour_court(jour), width=LARGEUR_COLONNE_JOUR,
                height=44, font=ctk.CTkFont(size=11, weight="bold")
            )
            if couleur_texte:
                lbl.configure(text_color=couleur_texte)
            lbl.grid(row=0, column=col, padx=2, pady=2)

        for chambre in chambres:
            row_frame = ctk.CTkFrame(self.grille_scroll, fg_color="transparent")
            row_frame.pack(anchor="w")

            info_frame = ctk.CTkFrame(
                row_frame, width=LARGEUR_COLONNE_CHAMBRE, height=44, corner_radius=6,
                fg_color=("gray88", "gray20")
            )
            info_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
            info_frame.grid_propagate(False)
            ctk.CTkLabel(
                info_frame, text=f"N°{chambre.numero}\n{chambre.type}",
                font=ctk.CTkFont(size=11, weight="bold"), justify="left"
            ).place(relx=0.05, rely=0.5, anchor="w")

            occ_chambre = occupations.get(chambre.id, {})
            for col, jour in enumerate(jours, start=1):
                reservation = occ_chambre.get(jour)
                est_aujourdhui = jour == today_str
                self._construire_cellule(
                    row_frame, chambre.id, jour, reservation, est_aujourdhui, row=0, col=col
                )
                