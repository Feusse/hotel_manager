# FICHIER: dashboard_view.py
"""
Vue : Tableau de bord.
Vue d'ensemble en lecture seule : occupation, revenus du mois,
arrivées/départs du jour, top clients, répartition par type de chambre.
"""

import customtkinter as ctk

from controllers.dashboard_controller import DashboardController

COULEUR_STATUT_CHAMBRE = {
    "Disponible": "#2fa84f",
    "Occupée": "#d9534f",
    "Maintenance": "#f0ad4e",
}


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self._build_layout()
        self.refresh()

    def _build_layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Zone des cartes statistiques (haut)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")

        # Zone scrollable du bas (arrivées/départs/top clients/répartition)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)

    # ---------------------------------------------------------------
    def _stat_card(self, parent, titre, valeur, sous_texte=None, couleur="#1f6aa5"):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("gray92", "gray17"))
        ctk.CTkLabel(
            card, text=titre, text_color="gray", font=ctk.CTkFont(size=12)
        ).pack(padx=20, pady=(18, 2), anchor="w")
        ctk.CTkLabel(
            card, text=valeur, font=ctk.CTkFont(size=26, weight="bold"), text_color=couleur
        ).pack(padx=20, anchor="w")
        if sous_texte:
            ctk.CTkLabel(
                card, text=sous_texte, text_color="gray", font=ctk.CTkFont(size=11)
            ).pack(padx=20, pady=(0, 18), anchor="w")
        else:
            ctk.CTkLabel(card, text="").pack(pady=(0, 10))
        return card

    def _build_cartes(self, stats):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        occ = stats["occupation"]
        card1 = self._stat_card(
            self.cards_frame,
            "Taux d'occupation",
            f"{occ['pourcentage']}%",
            f"{occ['occupees']} / {occ['total']} chambres occupées",
            couleur="#1f6aa5"
        )
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        rev = stats["revenus_mois"]
        card2 = self._stat_card(
            self.cards_frame,
            "Revenus du mois",
            f"{rev['total']:.0f} XAF",
            f"Séjours {rev['sejours']:.0f} + Dépenses {rev['depenses']:.0f} XAF",
            couleur="#2fa84f"
        )
        card2.grid(row=0, column=1, sticky="nsew", padx=10)

        card3 = self._stat_card(
            self.cards_frame,
            "Réservations actives",
            str(stats["reservations_actives"]),
            f"{len(stats['arrivees_aujourdhui'])} arrivée(s) et {len(stats['departs_aujourdhui'])} départ(s) aujourd'hui",
            couleur="#8a6d1f"
        )
        card3.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

    # ---------------------------------------------------------------
    def _section_frame(self, parent, titre):
        frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=("gray92", "gray17"))
        ctk.CTkLabel(
            frame, text=titre, font=ctk.CTkFont(size=15, weight="bold")
        ).pack(padx=20, pady=(18, 10), anchor="w")
        return frame

    def _build_arrivees_departs(self, stats):
        arrivees = stats["arrivees_aujourdhui"]
        departs = stats["departs_aujourdhui"]

        frame_arrivees = self._section_frame(self.scroll_frame, "🛬 Arrivées aujourd'hui")
        frame_arrivees.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 15))

        if not arrivees:
            ctk.CTkLabel(frame_arrivees, text="Aucune arrivée prévue aujourd'hui.",
                         text_color="gray").pack(padx=20, pady=(0, 18), anchor="w")
        else:
            for r in arrivees:
                ligne = ctk.CTkFrame(frame_arrivees, fg_color="transparent")
                ligne.pack(padx=20, pady=(0, 10), fill="x")
                ctk.CTkLabel(
                    ligne, text=f"{r['client_prenom']} {r['client_nom']}",
                    font=ctk.CTkFont(weight="bold"), anchor="w"
                ).pack(anchor="w")
                ctk.CTkLabel(
                    ligne, text=f"Chambre {r['chambre_numero']}  •  jusqu'au {r['date_depart']}",
                    text_color="gray", anchor="w"
                ).pack(anchor="w")
            ctk.CTkLabel(frame_arrivees, text="").pack(pady=(0, 8))

        frame_departs = self._section_frame(self.scroll_frame, "🛫 Départs aujourd'hui")
        frame_departs.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 15))

        if not departs:
            ctk.CTkLabel(frame_departs, text="Aucun départ prévu aujourd'hui.",
                         text_color="gray").pack(padx=20, pady=(0, 18), anchor="w")
        else:
            for r in departs:
                ligne = ctk.CTkFrame(frame_departs, fg_color="transparent")
                ligne.pack(padx=20, pady=(0, 10), fill="x")
                ctk.CTkLabel(
                    ligne, text=f"{r['client_prenom']} {r['client_nom']}",
                    font=ctk.CTkFont(weight="bold"), anchor="w"
                ).pack(anchor="w")
                ctk.CTkLabel(
                    ligne, text=f"Chambre {r['chambre_numero']}  •  arrivé(e) le {r['date_arrivee']}",
                    text_color="gray", anchor="w"
                ).pack(anchor="w")
            ctk.CTkLabel(frame_departs, text="").pack(pady=(0, 8))

    def _build_top_clients(self, stats):
        top = stats["top_clients"]
        frame = self._section_frame(self.scroll_frame, "🏆 Top clients (par montant total)")
        frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 15))

        if not top:
            ctk.CTkLabel(frame, text="Aucune donnée disponible.",
                         text_color="gray").pack(padx=20, pady=(0, 18), anchor="w")
            return

        for i, r in enumerate(top, start=1):
            total = r["total_sejours"] + r["total_depenses"]
            ligne = ctk.CTkFrame(frame, fg_color="transparent")
            ligne.pack(padx=20, pady=(0, 10), fill="x")
            ligne.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                ligne, text=f"#{i}", width=30, font=ctk.CTkFont(weight="bold"), text_color="#1f6aa5"
            ).grid(row=0, column=0, rowspan=2, sticky="w")

            ctk.CTkLabel(
                ligne, text=f"{r['prenom']} {r['nom']}", font=ctk.CTkFont(weight="bold"), anchor="w"
            ).grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(
                ligne, text=f"{r['nb_sejours']} séjour(s)  •  {total:.2f} XAF au total",
                text_color="gray", anchor="w"
            ).grid(row=1, column=1, sticky="w")

        ctk.CTkLabel(frame, text="").pack(pady=(0, 8))

    def _build_repartition(self, stats):
        repartition = stats["repartition_types"]
        frame = self._section_frame(self.scroll_frame, "🛏️ Occupation par type de chambre")
        frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0), pady=(0, 15))

        if not repartition:
            ctk.CTkLabel(frame, text="Aucune chambre enregistrée.",
                         text_color="gray").pack(padx=20, pady=(0, 18), anchor="w")
            return

        for type_chambre, valeurs in repartition.items():
            total = valeurs["total"]
            occupees = valeurs["occupees"]
            ratio = occupees / total if total > 0 else 0

            bloc = ctk.CTkFrame(frame, fg_color="transparent")
            bloc.pack(padx=20, pady=(0, 12), fill="x")

            ctk.CTkLabel(
                bloc, text=f"{type_chambre}  ({occupees}/{total})",
                anchor="w", font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w")

            barre_fond = ctk.CTkFrame(bloc, height=10, corner_radius=5, fg_color=("gray80", "gray30"))
            barre_fond.pack(fill="x", pady=(4, 0))
            barre_fond.pack_propagate(False)

            if ratio > 0:
                barre_remplie = ctk.CTkFrame(
                    barre_fond, corner_radius=5, fg_color="#d9534f",
                    width=1
                )
                barre_remplie.place(relx=0, rely=0, relwidth=ratio, relheight=1)

        ctk.CTkLabel(frame, text="").pack(pady=(0, 8))

    # ---------------------------------------------------------------
    def refresh(self):
        stats = DashboardController.obtenir_statistiques()

        self._build_cartes(stats)

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self._build_arrivees_departs(stats)
        self._build_top_clients(stats)
        self._build_repartition(stats)
        