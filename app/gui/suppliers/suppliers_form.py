from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.suppliers import supplier_provider


class SuppliersForm(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)

        self.app = app
        self.parent = parent
        self.provider = supplier_provider
        self.main_container = main_container
        self.selected_supplier_id = None

        self.setup_ui()


    def setup_ui(self):
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.setup_form_section()
        self.setup_btn_actions()


    def setup_form_section(self):

        ttk.Label(
            self.right_frame,
            text="Datos del Proveedor",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 15))

        self.form_frame = ttk.Frame(self.right_frame)
        self.form_frame.pack(fill=X)

        # ID Field
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

        # Nombre de empresa
        ttk.Label(self.form_frame, text="Nombre Empresa:*").pack(anchor=W, pady=(10, 2))
        self.name_var = ttk.StringVar()
        self.name_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.pack(fill=X, pady=(0, 5))

        # Nombre de contacto
        ttk.Label(self.form_frame, text="Persona de Contacto:").pack(anchor=W, pady=(5, 2))
        self.contact_var = ttk.StringVar()
        self.contact_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.contact_var,
            width=30
        )
        self.contact_entry.pack(fill=X, pady=(0, 5))

        # Teléfono
        ttk.Label(self.form_frame, text="Teléfono:").pack(anchor=W, pady=(5, 2))
        self.phone_var = ttk.StringVar()
        self.phone_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.phone_var,
            width=30
        )
        self.phone_entry.pack(fill=X, pady=(0, 5))

        # Email
        ttk.Label(self.form_frame, text="Email:").pack(anchor=W, pady=(5, 2))
        self.email_var = ttk.StringVar()
        self.email_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.email_var,
            width=30
        )
        self.email_entry.pack(fill=X, pady=(0, 5))

        # Dirección
        ttk.Label(self.form_frame, text="Dirección:").pack(anchor=W, pady=(5, 2))
        self.address_var = ttk.StringVar()
        self.address_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.address_var,
            width=30
        )
        self.address_entry.pack(fill=X, pady=(0, 5))

        # Ciudad
        ttk.Label(self.form_frame, text="Ciudad:").pack(anchor=W, pady=(5, 2))
        self.city_var = ttk.StringVar()
        self.city_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.city_var,
            width=30
        )
        self.city_entry.pack(fill=X, pady=(0, 5))

        # Tipo de producto
        ttk.Label(self.form_frame, text="Tipo de Producto:").pack(anchor=W, pady=(5, 2))
        self.product_type_var = ttk.StringVar()
        self.product_type_combo = ttk.Combobox(
            self.form_frame,
            textvariable=self.product_type_var,
            values=["Maíz", "Harina", "Aceites", "Empaques", "Maquinaria", "Insumos Varios", "Otro"],
            width=28
        )
        self.product_type_combo.pack(fill=X, pady=(0, 5))

        # Notas
        ttk.Label(self.form_frame, text="Notas:").pack(anchor=W, pady=(5, 2))
        self.notes_text = ttk.Text(
            self.form_frame,
            height=3,
            width=30
        )
        self.notes_text.pack(fill=X, pady=(0, 10))


    def setup_btn_actions(self):

        btn_container = ttk.Frame(self.right_frame)
        btn_container.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_container,
            text="Nuevo",
            command=self.new_supplier,
            bootstyle="success",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Guardar",
            command=self.save_supplier,
            bootstyle="primary",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Eliminar",
            command=self.delete_supplier,
            bootstyle="danger",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Limpiar",
            command=self.clear_form,
            bootstyle="secondary-outline",
            width=20
        ).pack(fill=X, pady=5)


    def new_supplier(self):
        self.clear_form()
        self.name_entry.focus()


    def save_supplier(self):

        name = self.name_var.get().strip()
        contact_name = self.contact_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_var.get().strip()
        city = self.city_var.get().strip()
        product_type = self.product_type_var.get().strip()
        notes = self.notes_text.get('1.0', 'end-1c').strip()

        if not name:
            messagebox.showerror("Error", "El nombre de la empresa es obligatorio")
            self.name_entry.focus()
            return

        if self.selected_supplier_id is None:

            success, result = self.provider.add(
                name, contact_name, phone, email, address, city, product_type, notes
            )

            if success:
                messagebox.showinfo("Éxito", "Proveedor creado exitosamente")
                self.clear_form()

                if hasattr(self.parent, 'table_section'):
                    self.parent.table_section.load_suppliers()
            else:
                messagebox.showerror("Error", f"No se pudo crear el proveedor: {result}")
        else:
            # Update existing supplier
            success, result = self.provider.update(
                self.selected_supplier_id, name, contact_name, phone, email,
                address, city, product_type, notes
            )
            if success:
                messagebox.showinfo("Éxito", "Proveedor actualizado exitosamente")
                self.clear_form()

                if hasattr(self.parent, 'table_section'):
                    self.parent.table_section.load_suppliers()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el proveedor: {result}")


    def delete_supplier(self):

        if self.selected_supplier_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor para eliminar")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al proveedor '{self.name_var.get()}'?"
        )

        if not confirm:
            return

        success, result = self.provider.delete(self.selected_supplier_id)

        if success:
            messagebox.showinfo("Éxito", "Proveedor eliminado exitosamente")
            self.clear_form()

            if hasattr(self.parent, 'table_section'):
                self.parent.table_section.load_suppliers()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar el proveedor: {result}")


    def clear_form(self):

        self.selected_supplier_id = None
        self.id_label.config(text="Nuevo")
        self.name_var.set("")
        self.contact_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.city_var.set("")
        self.product_type_var.set("")
        self.notes_text.delete('1.0', 'end')

        if hasattr(self.parent, 'table_section'):
            self.parent.table_section.clear_selection()
