from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.dealers import dealer_provider


class DealersForm(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)

        self.app = app
        self.parent = parent
        self.provider = dealer_provider
        self.main_container = main_container
        self.selected_dealer_id = None

        self.setup_ui()

    def setup_ui(self):
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.setup_form_section()
        self.setup_btn_actions()

    def setup_form_section(self):

        ttk.Label(
            self.right_frame,
            text="Datos del Repartidor",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 15))

        self.form_frame = ttk.Frame(self.right_frame)
        self.form_frame.pack(fill=X)

        # ID
        id_frame = ttk.Frame(self.form_frame)
        id_frame.pack(fill=X, pady=5)

        ttk.Label(id_frame, text="ID:", width=12).pack(side=LEFT)
        self.id_label = ttk.Label(
            id_frame,
            text="Nuevo",
            font=("Arial", 10, "bold"),
            bootstyle="info"
        )
        self.id_label.pack(side=LEFT)

        # Nombre
        ttk.Label(self.form_frame, text="Nombre:*").pack(anchor=W, pady=(10, 2))
        self.name_var = ttk.StringVar()
        self.name_entry = ttk.Entry(self.form_frame, textvariable=self.name_var, width=30)
        self.name_entry.pack(fill=X, pady=(0, 5))

        # Usuario
        ttk.Label(self.form_frame, text="Usuario:*").pack(anchor=W, pady=(5, 2))
        self.username_var = ttk.StringVar()
        self.username_entry = ttk.Entry(self.form_frame, textvariable=self.username_var, width=30)
        self.username_entry.pack(fill=X, pady=(0, 5))

        # PIN
        ttk.Label(self.form_frame, text="PIN:*").pack(anchor=W, pady=(5, 2))
        self.pin_var = ttk.StringVar()
        self.pin_entry = ttk.Entry(self.form_frame, textvariable=self.pin_var, width=30)
        self.pin_entry.pack(fill=X, pady=(0, 5))

    def setup_btn_actions(self):

        btn_container = ttk.Frame(self.right_frame)
        btn_container.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_container, text="Nuevo", command=self.new_dealer,
            bootstyle="success", width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container, text="Guardar", command=self.save_dealer,
            bootstyle="primary", width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container, text="Eliminar", command=self.delete_dealer,
            bootstyle="danger", width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container, text="Limpiar", command=self.clear_form,
            bootstyle="secondary-outline", width=20
        ).pack(fill=X, pady=5)

    def new_dealer(self):
        self.clear_form()
        self.name_entry.focus()

    def save_dealer(self):

        name = self.name_var.get().strip()
        username = self.username_var.get().strip()
        pin = self.pin_var.get().strip()

        if not name or not username or not pin:
            messagebox.showerror("Error", "Nombre, usuario y PIN son obligatorios")
            return

        if self.selected_dealer_id is None:
            success, result = self.provider.add(username, pin, name)
            msg = "Repartidor creado exitosamente"
        else:
            success, result = self.provider.update(self.selected_dealer_id, username, pin, name)
            msg = "Repartidor actualizado exitosamente"

        if success:
            messagebox.showinfo("Éxito", msg)
            self.clear_form()
            if hasattr(self.parent, 'table_section'):
                self.parent.table_section.load_dealers()
        else:
            messagebox.showerror("Error", str(result))

    def delete_dealer(self):

        if self.selected_dealer_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un repartidor para eliminar")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al repartidor '{self.name_var.get()}'?"
        )

        if not confirm:
            return

        success, result = self.provider.delete(self.selected_dealer_id)

        if success:
            messagebox.showinfo("Éxito", "Repartidor eliminado exitosamente")
            self.clear_form()
            if hasattr(self.parent, 'table_section'):
                self.parent.table_section.load_dealers()
        else:
            messagebox.showerror("Error", str(result))

    def clear_form(self):

        self.selected_dealer_id = None
        self.id_label.config(text="Nuevo")
        self.name_var.set("")
        self.username_var.set("")
        self.pin_var.set("")

        if hasattr(self.parent, 'table_section'):
            self.parent.table_section.clear_selection()
