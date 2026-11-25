# FICHIER: main_window.py
"""
Fenêtre principale : sidebar de navigation + zone de contenu dynamique.
"""

import customtkinter as ctk

from views.dashboard_view import DashboardView
from views.chambres_view import ChambresView
from views.clients_view import ClientsView
from views.reservations_view import ReservationsView
from views.factures_view import FacturesView
from views.planning_view import PlanningView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hôtel Manager — Système de Réservation")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        self.current_view = None
        self._preselection_reservation = None
        self.show_view("dashboard")

    # ---------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("gray90", "gray13"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="🏨 KRYSTAL PALACE Hôtel",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(padx=20, pady=(25, 30), anchor="w")

        self.nav_buttons = {}
        items = [
            ("dashboard", "📊  Tableau de bord"),
            ("planning", "🗓️  Planning"),
            ("chambres", "🛏️  Chambres"),
            ("clients", "👤  Clients"),
            ("reservations", "📅  Réservations"),
            ("factures", "🧾  Factures"),
        ]
        for key, label in items:
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", height=42,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(padx=15, pady=4, fill="x")
            self.nav_buttons[key] = btn

        footer = ctk.CTkLabel(
            sidebar, text="KRYSTAL PALACE Hôtel",
            text_color="gray", font=ctk.CTkFont(size=10)
        )
        footer.pack(side="bottom", pady=15)

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    # ---------------------------------------------------------------
    def _on_creneau_libre_selectionne(self, chambre_id, date_str):
        """Callback du planning : bascule vers Réservations avec pré-sélection."""
        self._preselection_reservation = {
            "chambre_id": chambre_id,
            "date_arrivee": date_str,
        }
        self.show_view("reservations")

    def show_view(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=("gray75", "gray30"))
            else:
                btn.configure(fg_color="transparent")

        if self.current_view is not None:
            self.current_view.destroy()

        if key == "dashboard":
            self.current_view = DashboardView(self.content_frame)
        elif key == "planning":
            self.current_view = PlanningView(
                self.content_frame, on_creneau_libre=self._on_creneau_libre_selectionne
            )
        elif key == "chambres":
            self.current_view = ChambresView(self.content_frame)
        elif key == "clients":
            self.current_view = ClientsView(self.content_frame)
        elif key == "reservations":
            preselection = self._preselection_reservation
            self._preselection_reservation = None
            self.current_view = ReservationsView(self.content_frame, preselection=preselection)
        elif key == "factures":
            self.current_view = FacturesView(self.content_frame)
        else:
            raise ValueError(f"Vue inconnue : {key}")

        self.current_view.grid(row=0, column=0, sticky="nsew")
        
        