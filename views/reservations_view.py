# FICHIER: reservations_view.py
"""
Vue : Gestion des Réservations.
Formulaire avec calcul automatique (nuits, montant) et vérification
de disponibilité en temps réel avant validation.
Inclut la gestion des dépenses annexes du client durant son séjour.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

from controllers.reservation_controller import ReservationController
from controllers.client_controller import ClientController
from controllers.chambre_controller import ChambreController
from controllers.facture_controller import FactureController
from controllers.depense_controller import DepenseController
from utils.printer import imprimer_pdf, ImpressionError

COULEUR_STATUT = {
    "Confirmée": "#2fa84f",
    "Annulée": "#8a2e2e",
    "Terminée": "#4a4a4a",
}


class ReservationsView(ctk.CTkFrame):
    def __init__(self, master, preselection=None):
        """
        preselection : dict optionnel {'chambre_id': int, 'date_arrivee': 'YYYY-MM-DD'}
        transmis depuis le planning visuel quand l'utilisateur clique sur un créneau libre.
        """
        super().__init__(master, fg_color="transparent")
        self._build_layout()
        self._charger_listes_reference()
        self.refresh_liste()
        if preselection:
            self._appliquer_preselection(preselection)
    

    def _appliquer_preselection(self, preselection):
        chambre_id = preselection.get("chambre_id")
        date_arrivee = preselection.get("date_arrivee")

        if chambre_id is not None:
            for key, chambre in self.chambres_map.items():
                if chambre.id == chambre_id:
                    self.chambre_var.set(key)
                    break

        if date_arrivee:
            self.entry_arrivee.delete(0, "end")
            self.entry_arrivee.insert(0, date_arrivee)
            try:
                d = datetime.strptime(date_arrivee, "%Y-%m-%d")
                lendemain = (d + timedelta(days=1)).strftime("%Y-%m-%d")
                self.entry_depart.delete(0, "end")
                self.entry_depart.insert(0, lendemain)
            except ValueError:
                pass

        self._recalculer()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=6)
        self.grid_columnconfigure(0, weight=1)

        self._build_form_panel()
        self._build_list_panel()

    # ---------------------------------------------------------------
    def _build_form_panel(self):
        panel = ctk.CTkFrame(self, width=340, corner_radius=12)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 15))
        panel.grid_propagate(False)

        ctk.CTkLabel(panel, text="Nouvelle réservation",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(padx=20, pady=(20, 15), anchor="w")

        ctk.CTkLabel(panel, text="Client *", anchor="w").pack(padx=20, pady=(0, 2), anchor="w")
        self.client_var = ctk.StringVar(value="Aucun client")
        self.option_client = ctk.CTkOptionMenu(panel, values=["Aucun client"], variable=self.client_var,
                                                command=lambda _: self._recalculer())
        self.option_client.pack(padx=20, fill="x")

        ctk.CTkLabel(panel, text="Chambre *", anchor="w").pack(padx=20, pady=(10, 2), anchor="w")
        self.chambre_var = ctk.StringVar(value="Aucune chambre")
        self.option_chambre = ctk.CTkOptionMenu(panel, values=["Aucune chambre"], variable=self.chambre_var,
                                                 command=lambda _: self._recalculer())
        self.option_chambre.pack(padx=20, fill="x")

        ctk.CTkLabel(panel, text="Date d'arrivée (AAAA-MM-JJ) *", anchor="w").pack(padx=20, pady=(10, 2), anchor="w")
        self.entry_arrivee = ctk.CTkEntry(panel, placeholder_text="2026-07-10")
        self.entry_arrivee.pack(padx=20, fill="x")
        self.entry_arrivee.bind("<KeyRelease>", lambda e: self._recalculer())

        ctk.CTkLabel(panel, text="Date de départ (AAAA-MM-JJ) *", anchor="w").pack(padx=20, pady=(10, 2), anchor="w")
        self.entry_depart = ctk.CTkEntry(panel, placeholder_text="2026-07-13")
        self.entry_depart.pack(padx=20, fill="x")
        self.entry_depart.bind("<KeyRelease>", lambda e: self._recalculer())

        # --- Zone d'aperçu dynamique ---
        self.apercu_frame = ctk.CTkFrame(panel, corner_radius=10, fg_color=("gray88", "gray20"))
        self.apercu_frame.pack(padx=20, pady=(15, 10), fill="x")

        self.label_nuits = ctk.CTkLabel(self.apercu_frame, text="Nombre de nuits : —", anchor="w")
        self.label_nuits.pack(padx=15, pady=(12, 2), anchor="w")

        self.label_montant = ctk.CTkLabel(
            self.apercu_frame, text="Montant total : —",
            font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        )
        self.label_montant.pack(padx=15, pady=(0, 2), anchor="w")

        self.label_dispo = ctk.CTkLabel(self.apercu_frame, text="", anchor="w")
        self.label_dispo.pack(padx=15, pady=(2, 12), anchor="w")

        self.btn_valider = ctk.CTkButton(
            panel, text="Créer la réservation", command=self._on_valider,
            fg_color="#1f6aa5"
        )
        self.btn_valider.pack(padx=20, pady=(5, 20), fill="x")

    # ---------------------------------------------------------------
    def _build_list_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="Liste des réservations",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

        filtres = ctk.CTkFrame(panel, fg_color="transparent")
        filtres.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        ctk.CTkLabel(filtres, text="Statut :").pack(side="left", padx=(0, 5))
        self.filter_statut = ctk.StringVar(value="Toutes")
        ctk.CTkOptionMenu(
            filtres, values=["Toutes", "Confirmée", "Annulée", "Terminée"],
            variable=self.filter_statut, command=lambda _: self.refresh_liste(), width=140
        ).pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    # ---------------------------------------------------------------
    def _charger_listes_reference(self):
        """Charge les clients et chambres disponibles dans les menus déroulants."""
        clients = ClientController.lister()
        self.clients_map = {f"{c.prenom} {c.nom} (#{c.id})": c.id for c in clients}
        valeurs_clients = list(self.clients_map.keys()) or ["Aucun client - ajoutez-en un"]
        self.option_client.configure(values=valeurs_clients)
        self.client_var.set(valeurs_clients[0])

        chambres = ChambreController.lister()
        self.chambres_map = {
            f"N°{c.numero} - {c.type} ({c.prix_nuit:.2f} XAF/nuit)": c for c in chambres
        }
        valeurs_chambres = list(self.chambres_map.keys()) or ["Aucune chambre - ajoutez-en une"]
        self.option_chambre.configure(values=valeurs_chambres)
        self.chambre_var.set(valeurs_chambres[0])

        # Dates par défaut : aujourd'hui / demain
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.entry_arrivee.insert(0, today)
        self.entry_depart.insert(0, tomorrow)

    def _recalculer(self):
        """Recalcule en direct l'aperçu (nuits, montant, disponibilité)."""
        chambre_key = self.chambre_var.get()
        chambre = self.chambres_map.get(chambre_key)
        date_arrivee = self.entry_arrivee.get().strip()
        date_depart = self.entry_depart.get().strip()

        if not chambre or not date_arrivee or not date_depart:
            self.label_nuits.configure(text="Nombre de nuits : —")
            self.label_montant.configure(text="Montant total : —")
            self.label_dispo.configure(text="")
            return

        try:
            apercu = ReservationController.calculer_apercu(chambre.id, date_arrivee, date_depart)
            self.label_nuits.configure(text=f"Nombre de nuits : {apercu['nb_nuits']}")
            self.label_montant.configure(text=f"Montant total : {apercu['montant_total']:.2f} XAF")
            if apercu["disponible"]:
                self.label_dispo.configure(text="✅ Chambre disponible", text_color="#2fa84f")
                self.btn_valider.configure(state="normal")
            else:
                self.label_dispo.configure(text="❌ Chambre déjà réservée sur cette période", text_color="#d9534f")
                self.btn_valider.configure(state="disabled")
        except ValueError as e:
            self.label_nuits.configure(text="Nombre de nuits : —")
            self.label_montant.configure(text="Montant total : —")
            self.label_dispo.configure(text=f"⚠ {e}", text_color="#f0ad4e")
            self.btn_valider.configure(state="disabled")

    def _on_valider(self):
        client_key = self.client_var.get()
        chambre_key = self.chambre_var.get()
        client_id = self.clients_map.get(client_key)
        chambre = self.chambres_map.get(chambre_key)
        date_arrivee = self.entry_arrivee.get().strip()
        date_depart = self.entry_depart.get().strip()

        if not client_id or not chambre:
            messagebox.showerror("Erreur", "Veuillez sélectionner un client et une chambre valides.")
            return

        try:
            reservation_id, nb_nuits, montant = ReservationController.creer_reservation(
                client_id, chambre.id, date_arrivee, date_depart
            )
            messagebox.showinfo(
                "Réservation créée",
                f"Réservation confirmée pour {nb_nuits} nuit(s).\nMontant total : {montant:.2f} XAF"
            )
            self._charger_listes_reference()
            self.refresh_liste()
            self._recalculer()
        except ValueError as e:
            messagebox.showerror("Impossible de réserver", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    # ---------------------------------------------------------------
    def _on_annuler_reservation(self, res_id):
        confirm = messagebox.askyesno("Confirmation", "Annuler cette réservation ?")
        if confirm:
            try:
                ReservationController.annuler_reservation(res_id)
                self.refresh_liste()
                self._charger_listes_reference()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def _on_terminer_sejour(self, res_id):
        confirm = messagebox.askyesno("Confirmation", "Marquer ce séjour comme terminé (check-out) ?")
        if confirm:
            try:
                ReservationController.terminer_sejour(res_id)
                self.refresh_liste()
                self._charger_listes_reference()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def _on_generer_facture(self, res_id):
        try:
            filepath, numero = FactureController.generer(res_id)
            messagebox.showinfo(
                "Facture générée",
                f"Facture {numero} générée avec succès (séjour + dépenses inclus).\nEmplacement : {filepath}"
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer la facture : {e}")
    def _on_imprimer_derniere_facture(self, res_id):
        """Imprime la dernière facture générée pour cette réservation, si elle existe."""
        facture = FactureController.obtenir_pour_reservation(res_id)
        if facture is None:
            messagebox.showwarning(
                "Aucune facture",
                "Aucune facture n'a encore été générée pour cette réservation.\n"
                "Cliquez d'abord sur \"Facture PDF\"."
            )
            return
        try:
            imprimer_pdf(facture.chemin_pdf)
            messagebox.showinfo("Impression", "La facture a été envoyée à l'imprimante.")
        except ImpressionError as e:
            messagebox.showerror("Erreur d'impression", str(e))
            

    # ---------------------------------------------------------------
    def _on_gerer_depenses(self, reservation):
        """Ouvre une fenêtre pour ajouter/consulter/supprimer les dépenses d'une réservation."""
        win = ctk.CTkToplevel(self)
        win.title(f"Dépenses — {reservation['client_prenom']} {reservation['client_nom']}")
        win.geometry("520x560")
        win.grab_set()

        ctk.CTkLabel(
            win, text=f"Dépenses du séjour — Chambre {reservation['chambre_numero']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=20, pady=(20, 5), anchor="w")
        ctk.CTkLabel(
            win, text=f"Du {reservation['date_arrivee']} au {reservation['date_depart']}",
            text_color="gray"
        ).pack(padx=20, pady=(0, 15), anchor="w")

        # --- Formulaire d'ajout ---
        form_frame = ctk.CTkFrame(win, corner_radius=10, fg_color=("gray88", "gray20"))
        form_frame.pack(padx=20, pady=(0, 15), fill="x")

        ctk.CTkLabel(form_frame, text="Description (ex: Minibar, Restaurant, Spa...)", anchor="w").pack(
            padx=15, pady=(12, 2), anchor="w"
        )
        entry_description = ctk.CTkEntry(form_frame, placeholder_text="Ex: Dîner restaurant")
        entry_description.pack(padx=15, fill="x")

        ctk.CTkLabel(form_frame, text="Montant (XAF)", anchor="w").pack(padx=15, pady=(10, 2), anchor="w")
        entry_montant = ctk.CTkEntry(form_frame, placeholder_text="Ex: 250")
        entry_montant.pack(padx=15, fill="x")

        label_erreur = ctk.CTkLabel(form_frame, text="", text_color="#d9534f")
        label_erreur.pack(padx=15, pady=(8, 0), anchor="w")

        def rafraichir_liste_depenses():
            for widget in scroll_depenses.winfo_children():
                widget.destroy()

            depenses = DepenseController.lister(reservation["id"])
            if not depenses:
                ctk.CTkLabel(scroll_depenses, text="Aucune dépense enregistrée.",
                             text_color="gray").pack(pady=15)
            else:
                for d in depenses:
                    ligne = ctk.CTkFrame(scroll_depenses, corner_radius=8, fg_color=("gray92", "gray17"))
                    ligne.pack(fill="x", pady=3, padx=2)
                    ligne.grid_columnconfigure(0, weight=1)

                    info = ctk.CTkFrame(ligne, fg_color="transparent")
                    info.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
                    ctk.CTkLabel(info, text=d.description, anchor="w",
                                 font=ctk.CTkFont(weight="bold")).pack(anchor="w")
                    date_aff = d.date_depense.split(" ")[0] if d.date_depense else ""
                    ctk.CTkLabel(info, text=f"{d.montant:.2f} MAD  •  {date_aff}",
                                 text_color="gray", anchor="w").pack(anchor="w")

                    ctk.CTkButton(
                        ligne, text="✕", width=30, height=28,
                        fg_color="#8a2e2e", hover_color="#a53838",
                        command=lambda did=d.id: supprimer_depense(did)
                    ).grid(row=0, column=1, padx=10, pady=8)

            total = DepenseController.total(reservation["id"])
            label_total.configure(text=f"Total des dépenses : {total:.2f} XAF")

        def ajouter_depense():
            description = entry_description.get().strip()
            montant = entry_montant.get().strip()
            try:
                DepenseController.ajouter(reservation["id"], description, montant)
                entry_description.delete(0, "end")
                entry_montant.delete(0, "end")
                label_erreur.configure(text="")
                rafraichir_liste_depenses()
            except ValueError as e:
                label_erreur.configure(text=str(e))

        def supprimer_depense(depense_id):
            confirm = messagebox.askyesno("Confirmation", "Supprimer cette dépense ?", parent=win)
            if confirm:
                DepenseController.supprimer(depense_id)
                rafraichir_liste_depenses()

        ctk.CTkButton(
            form_frame, text="Ajouter la dépense", command=ajouter_depense,
            fg_color="#1f6aa5"
        ).pack(padx=15, pady=(10, 15), fill="x")

        # --- Liste des dépenses ---
        ctk.CTkLabel(win, text="Dépenses enregistrées", font=ctk.CTkFont(weight="bold")).pack(
            padx=20, anchor="w"
        )
        scroll_depenses = ctk.CTkScrollableFrame(win, height=200)
        scroll_depenses.pack(padx=20, pady=(5, 10), fill="both", expand=True)

        label_total = ctk.CTkLabel(
            win, text="Total des dépenses : 0.00 XAF",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label_total.pack(padx=20, pady=(0, 20), anchor="w")

        rafraichir_liste_depenses()

    # ---------------------------------------------------------------
    def refresh_liste(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        statut = self.filter_statut.get()
        reservations = ReservationController.lister(statut if statut != "Toutes" else None)

        if not reservations:
            ctk.CTkLabel(self.scroll_frame, text="Aucune réservation trouvée.",
                         text_color="gray").pack(pady=20)
            return

        for r in reservations:
            self._build_card(r)

    def _build_card(self, r):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color=("gray92", "gray17"))
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)

        badge = ctk.CTkLabel(
            card, text=r["statut"], fg_color=COULEUR_STATUT.get(r["statut"], "gray"),
            text_color="white", corner_radius=6, width=90,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        badge.grid(row=0, column=0, rowspan=2, padx=15, pady=15, sticky="w")

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", pady=(15, 0))
        ctk.CTkLabel(
            info, text=f"{r['client_prenom']} {r['client_nom']}  —  Chambre {r['chambre_numero']} ({r['chambre_type']})",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w"
        ).pack(anchor="w")

        total_depenses = DepenseController.total(r["id"])
        texte_depenses = f"  •  Dépenses : {total_depenses:.2f} MAD" if total_depenses > 0 else ""
        ctk.CTkLabel(
            info,
            text=f"Du {r['date_arrivee']} au {r['date_depart']}  •  {r['nb_nuits']} nuit(s)  •  "
                 f"Séjour : {r['montant_total']:.2f} XAF{texte_depenses}",
            text_color="gray", anchor="w"
        ).pack(anchor="w", pady=(0, 15))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=15, pady=15)

        ctk.CTkButton(
            actions, text="Dépenses", width=100, height=28,
            fg_color="#8a6d1f", hover_color="#a0821f",
            command=lambda res=r: self._on_gerer_depenses(res)
        ).pack(pady=(0, 6))

        ctk.CTkButton(
            actions, text="Facture PDF", width=100, height=28,
            fg_color="#2a5d34", hover_color="#347040",
            command=lambda rid=r["id"]: self._on_generer_facture(rid)
        ).pack(pady=(0, 6))

        ctk.CTkButton(
            actions, text="Imprimer", width=100, height=28,
            fg_color="#1f6aa5", hover_color="#2a7fc1",
            command=lambda rid=r["id"]: self._on_imprimer_derniere_facture(rid)
        ).pack(pady=(0, 6))

        if r["statut"] == "Confirmée":
            ctk.CTkButton(
                actions, text="Check-out", width=100, height=28,
                fg_color="#3b3b3b", hover_color="#4d4d4d",
                command=lambda rid=r["id"]: self._on_terminer_sejour(rid)
            ).pack(pady=(0, 6))
            ctk.CTkButton(
                actions, text="Annuler", width=100, height=28,
                fg_color="#8a2e2e", hover_color="#a53838",
                command=lambda rid=r["id"]: self._on_annuler_reservation(rid)
            ).pack()