"""
Vue : Gestion des Chambres.
CRUD complet + filtres par type et statut + gestion photo.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import shutil
import os

from controllers.chambre_controller import (
    ChambreController, TYPES_CHAMBRE, STATUTS_CHAMBRE
)

PHOTOS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "photos"
)
os.makedirs(PHOTOS_DIR, exist_ok=True)

COULEUR_STATUT = {
    "Disponible": "#2fa84f",
    "Occupée": "#d9534f",
    "Maintenance": "#f0ad4e",
}


class ChambresView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.selected_photo_path = None
        self.editing_id = None

        self._build_layout()
        self.refresh_liste()

    # ---------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_form_panel()
        self._build_list_panel()

    # ---------------------------------------------------------------
    def _build_form_panel(self):
        panel = ctk.CTkFrame(self, width=320, corner_radius=12)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 15), pady=0)
        panel.grid_propagate(False)

        title = ctk.CTkLabel(panel, text="Ajouter / Modifier une chambre",
                              font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(padx=20, pady=(20, 15), anchor="w")

        self.entry_numero = self._labeled_entry(panel, "Numéro de chambre *")
        self.option_type = self._labeled_option(panel, "Type *", TYPES_CHAMBRE)
        self.entry_prix = self._labeled_entry(panel, "Prix / nuit (XAF) *")
        self.option_statut = self._labeled_option(panel, "Statut", STATUTS_CHAMBRE)

        ctk.CTkLabel(panel, text="Description", anchor="w").pack(
            padx=20, pady=(10, 2), anchor="w"
        )
        self.textbox_description = ctk.CTkTextbox(panel, height=70)
        self.textbox_description.pack(padx=20, pady=(0, 10), fill="x")

        photo_frame = ctk.CTkFrame(panel, fg_color="transparent")
        photo_frame.pack(padx=20, pady=(0, 10), fill="x")
        self.btn_photo = ctk.CTkButton(
            photo_frame, text="📷 Choisir une photo", command=self._choisir_photo,
            fg_color="#3b3b3b", hover_color="#4d4d4d"
        )
        self.btn_photo.pack(side="left")
        self.label_photo = ctk.CTkLabel(photo_frame, text="Aucune photo", text_color="gray")
        self.label_photo.pack(side="left", padx=10)

        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(15, 20), fill="x")

        self.btn_valider = ctk.CTkButton(
            btn_frame, text="Ajouter la chambre", command=self._on_valider,
            fg_color="#1f6aa5"
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
        entry.pack(padx=20, pady=(0, 0), fill="x")
        return entry

    def _labeled_option(self, parent, label_text, values):
        ctk.CTkLabel(parent, text=label_text, anchor="w").pack(padx=20, pady=(10, 2), anchor="w")
        var = ctk.StringVar(value=values[0])
        option = ctk.CTkOptionMenu(parent, values=values, variable=var)
        option.pack(padx=20, pady=(0, 0), fill="x")
        return option

    # ---------------------------------------------------------------
    def _build_list_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="Liste des chambres",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

        filtres = ctk.CTkFrame(panel, fg_color="transparent")
        filtres.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(filtres, text="Type :").pack(side="left", padx=(0, 5))
        self.filter_type = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(
            filtres, values=["Tous"] + TYPES_CHAMBRE, variable=self.filter_type,
            command=lambda _: self.refresh_liste(), width=120
        ).pack(side="left", padx=(0, 15))

        ctk.CTkLabel(filtres, text="Statut :").pack(side="left", padx=(0, 5))
        self.filter_statut = ctk.StringVar(value="Tous")
        ctk.CTkOptionMenu(
            filtres, values=["Tous"] + STATUTS_CHAMBRE, variable=self.filter_statut,
            command=lambda _: self.refresh_liste(), width=120
        ).pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    # ---------------------------------------------------------------
    def _choisir_photo(self):
        path = filedialog.askopenfilename(
            title="Choisir une photo",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")]
        )
        if path:
            self.selected_photo_path = path
            self.label_photo.configure(text=os.path.basename(path), text_color="white")

    def _reset_form(self):
        self.editing_id = None
        self.entry_numero.delete(0, "end")
        self.entry_prix.delete(0, "end")
        self.option_type.set(TYPES_CHAMBRE[0])
        self.option_statut.set(STATUTS_CHAMBRE[0])
        self.textbox_description.delete("1.0", "end")
        self.selected_photo_path = None
        self.label_photo.configure(text="Aucune photo", text_color="gray")
        self.btn_valider.configure(text="Ajouter la chambre")
        self.btn_annuler.configure(state="disabled")

    def _copier_photo(self, source_path, numero):
        if not source_path:
            return None
        ext = os.path.splitext(source_path)[1]
        dest_name = f"chambre_{numero}{ext}"
        dest_path = os.path.join(PHOTOS_DIR, dest_name)
        try:
            shutil.copy(source_path, dest_path)
            return dest_path
        except Exception:
            return None

    def _on_valider(self):
        numero = self.entry_numero.get().strip()
        type_ = self.option_type.get()
        prix = self.entry_prix.get().strip()
        statut = self.option_statut.get()
        description = self.textbox_description.get("1.0", "end").strip()

        photo_path = None
        if self.selected_photo_path:
            photo_path = self._copier_photo(self.selected_photo_path, numero)

        try:
            if self.editing_id is None:
                ChambreController.ajouter(numero, type_, prix, statut, description, photo_path)
                messagebox.showinfo("Succès", "Chambre ajoutée avec succès.")
            else:
                # Si aucune nouvelle photo choisie, on garde l'ancienne
                if photo_path is None:
                    chambre = ChambreController.obtenir(self.editing_id)
                    photo_path = chambre.photo_path if chambre else None
                ChambreController.modifier(
                    self.editing_id, numero, type_, prix, statut, description, photo_path
                )
                messagebox.showinfo("Succès", "Chambre modifiée avec succès.")
            self._reset_form()
            self.refresh_liste()
        except ValueError as e:
            messagebox.showerror("Erreur de validation", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    def _on_modifier(self, chambre):
        self.editing_id = chambre.id
        self.entry_numero.delete(0, "end")
        self.entry_numero.insert(0, chambre.numero)
        self.option_type.set(chambre.type)
        self.entry_prix.delete(0, "end")
        self.entry_prix.insert(0, str(chambre.prix_nuit))
        self.option_statut.set(chambre.statut)
        self.textbox_description.delete("1.0", "end")
        self.textbox_description.insert("1.0", chambre.description or "")
        self.selected_photo_path = None
        self.label_photo.configure(
            text=os.path.basename(chambre.photo_path) if chambre.photo_path else "Photo actuelle conservée",
            text_color="white" if chambre.photo_path else "gray"
        )
        self.btn_valider.configure(text="Enregistrer les modifications")
        self.btn_annuler.configure(state="normal")

    def _on_supprimer(self, chambre):
        confirm = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer la chambre {chambre.numero} ?\n"
            "Cette action est irréversible."
        )
        if confirm:
            try:
                ChambreController.supprimer(chambre.id)
                self.refresh_liste()
            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    f"Impossible de supprimer cette chambre (peut-être liée à des réservations) : {e}"
                )

    # ---------------------------------------------------------------
    def refresh_liste(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        chambres = ChambreController.lister(
            self.filter_type.get(), self.filter_statut.get()
        )

        if not chambres:
            ctk.CTkLabel(self.scroll_frame, text="Aucune chambre trouvée.",
                         text_color="gray").pack(pady=20)
            return

        for chambre in chambres:
            self._build_card(chambre)

    def _build_card(self, chambre):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color=("gray92", "gray17"))
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)

        badge_color = COULEUR_STATUT.get(chambre.statut, "gray")
        badge = ctk.CTkLabel(
            card, text=chambre.statut, fg_color=badge_color, text_color="white",
            corner_radius=6, width=90, font=ctk.CTkFont(size=11, weight="bold")
        )
        badge.grid(row=0, column=0, rowspan=2, padx=15, pady=15, sticky="w")

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", pady=(15, 0))
        ctk.CTkLabel(
            info_frame, text=f"Chambre {chambre.numero}  —  {chambre.type}",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_frame, text=f"{chambre.prix_nuit:.2f} XAF / nuit",
            text_color="gray", anchor="w"
        ).pack(anchor="w")

        if chambre.description:
            desc_label = ctk.CTkLabel(
                card, text=chambre.description, text_color="gray",
                anchor="w", wraplength=400, justify="left"
            )
            desc_label.grid(row=1, column=1, sticky="ew", pady=(0, 15), padx=(0, 10))
        else:
            spacer = ctk.CTkLabel(card, text="")
            spacer.grid(row=1, column=1, pady=(0, 15))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=15, pady=15)

        ctk.CTkButton(
            actions, text="Modifier", width=90, height=28,
            fg_color="#3b3b3b", hover_color="#4d4d4d",
            command=lambda c=chambre: self._on_modifier(c)
        ).pack(pady=(0, 6))

        ctk.CTkButton(
            actions, text="Supprimer", width=90, height=28,
            fg_color="#8a2e2e", hover_color="#a53838",
            command=lambda c=chambre: self._on_supprimer(c)
        ).pack()
