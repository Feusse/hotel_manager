"""
Vue : Gestion des Clients.
CRUD complet + recherche + historique des séjours.
"""

import customtkinter as ctk
from tkinter import messagebox

from controllers.client_controller import ClientController


class ClientsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.editing_id = None

        self._build_layout()
        self.refresh_liste()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_form_panel()
        self._build_list_panel()

    def _build_form_panel(self):
        panel = ctk.CTkFrame(self, width=320, corner_radius=12)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 15))
        panel.grid_propagate(False)

        ctk.CTkLabel(panel, text="Ajouter / Modifier un client",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(padx=20, pady=(20, 15), anchor="w")

        self.entry_nom = self._labeled_entry(panel, "Nom *")
        self.entry_prenom = self._labeled_entry(panel, "Prénom *")
        self.entry_telephone = self._labeled_entry(panel, "Téléphone")
        self.entry_email = self._labeled_entry(panel, "Email")
        self.entry_piece = self._labeled_entry(panel, "Pièce d'identité (CIN/Passeport)")
        self.entry_nationalite = self._labeled_entry(panel, "Nationalité")

        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(20, 20), fill="x")

        self.btn_valider = ctk.CTkButton(
            btn_frame, text="Ajouter le client", command=self._on_valider, fg_color="#1f6aa5"
        )
        self.btn_valider.pack(fill="x", pady=(0, 8))

        self.btn_annuler = ctk.CTkButton(
            btn_frame, text="Annuler la modification", command=self._reset_form,
            fg_color="transparent", border_width=1, text_color=("gray10", "gray90")
        )
        self.btn_annuler.pack(fill="x")
        self.btn_annuler.configure(state="disabled")

    def _labeled_entry(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, anchor="w").pack(padx=20, pady=(10, 2), anchor="w")
        entry = ctk.CTkEntry(parent)
        entry.pack(padx=20, fill="x")
        return entry

    def _build_list_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="Liste des clients",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

        search_frame = ctk.CTkFrame(panel, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="🔍 Rechercher (nom, prénom, téléphone, email)...",
            textvariable=self.search_var
        )
        self.search_entry.pack(fill="x")
        self.search_var.trace_add("write", lambda *args: self.refresh_liste())

        self.scroll_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _reset_form(self):
        self.editing_id = None
        for entry in [self.entry_nom, self.entry_prenom, self.entry_telephone,
                      self.entry_email, self.entry_piece, self.entry_nationalite]:
            entry.delete(0, "end")
        self.btn_valider.configure(text="Ajouter le client")
        self.btn_annuler.configure(state="disabled")

    def _on_valider(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        telephone = self.entry_telephone.get().strip()
        email = self.entry_email.get().strip()
        piece = self.entry_piece.get().strip()
        nationalite = self.entry_nationalite.get().strip()

        try:
            if self.editing_id is None:
                ClientController.ajouter(nom, prenom, telephone, email, piece, nationalite)
                messagebox.showinfo("Succès", "Client ajouté avec succès.")
            else:
                ClientController.modifier(
                    self.editing_id, nom, prenom, telephone, email, piece, nationalite
                )
                messagebox.showinfo("Succès", "Client modifié avec succès.")
            self._reset_form()
            self.refresh_liste()
        except ValueError as e:
            messagebox.showerror("Erreur de validation", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    def _on_modifier(self, client):
        self.editing_id = client.id
        self.entry_nom.delete(0, "end"); self.entry_nom.insert(0, client.nom)
        self.entry_prenom.delete(0, "end"); self.entry_prenom.insert(0, client.prenom)
        self.entry_telephone.delete(0, "end"); self.entry_telephone.insert(0, client.telephone or "")
        self.entry_email.delete(0, "end"); self.entry_email.insert(0, client.email or "")
        self.entry_piece.delete(0, "end"); self.entry_piece.insert(0, client.piece_identite or "")
        self.entry_nationalite.delete(0, "end"); self.entry_nationalite.insert(0, client.nationalite or "")
        self.btn_valider.configure(text="Enregistrer les modifications")
        self.btn_annuler.configure(state="normal")

    def _on_supprimer(self, client):
        confirm = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer {client.nom_complet} ?\nCette action est irréversible."
        )
        if confirm:
            try:
                ClientController.supprimer(client.id)
                self.refresh_liste()
            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    f"Impossible de supprimer ce client (il a peut-être des réservations liées) : {e}"
                )

    def _on_historique(self, client):
        historique = ClientController.historique(client.id)

        win = ctk.CTkToplevel(self)
        win.title(f"Historique de {client.nom_complet}")
        win.geometry("600x450")
        win.grab_set()

        ctk.CTkLabel(
            win, text=f"Historique des séjours — {client.nom_complet}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=20, pady=15, anchor="w")

        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not historique:
            ctk.CTkLabel(scroll, text="Aucun séjour enregistré.", text_color="gray").pack(pady=20)
            return

        for r in historique:
            card = ctk.CTkFrame(scroll, corner_radius=8, fg_color=("gray92", "gray17"))
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(
                card, text=f"Chambre {r['chambre_numero']} ({r['chambre_type']})",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(
                card, text=f"Du {r['date_arrivee']} au {r['date_depart']}  •  {r['nb_nuits']} nuit(s)",
                text_color="gray"
            ).pack(anchor="w", padx=15)
            ctk.CTkLabel(
                card, text=f"Montant : {r['montant_total']:.2f} MAD  •  Statut : {r['statut']}",
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=(0, 10))

    def refresh_liste(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        clients = ClientController.lister(self.search_var.get().strip() or None)

        if not clients:
            ctk.CTkLabel(self.scroll_frame, text="Aucun client trouvé.",
                         text_color="gray").pack(pady=20)
            return

        for client in clients:
            self._build_card(client)

    def _build_card(self, client):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color=("gray92", "gray17"))
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=0, sticky="ew", padx=15, pady=12)
        ctk.CTkLabel(
            info, text=client.nom_complet, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(anchor="w")
        details = " • ".join(filter(None, [client.telephone, client.email, client.nationalite]))
        ctk.CTkLabel(info, text=details or "Aucune information supplémentaire",
                     text_color="gray", anchor="w").pack(anchor="w")

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=1, padx=15, pady=12)

        ctk.CTkButton(
            actions, text="Historique", width=90, height=28,
            fg_color="#2a5d34", hover_color="#347040",
            command=lambda c=client: self._on_historique(c)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            actions, text="Modifier", width=80, height=28,
            fg_color="#3b3b3b", hover_color="#4d4d4d",
            command=lambda c=client: self._on_modifier(c)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            actions, text="Supprimer", width=80, height=28,
            fg_color="#8a2e2e", hover_color="#a53838",
            command=lambda c=client: self._on_supprimer(c)
        ).pack(side="left")
