

from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.inventory.products import ProductsInventory


class FormInventory(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.db = app.db
        self.main_container = main_container

        self.setup_ui()


    def setup_ui(self):
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.setup_form_section()


    def setup_form_section(self):
        """Configurar sección de formulario"""
        # Título del formulario
        ttk.Label(
            self.right_frame,
            text="Gestión de Producto",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        # Formulario
        form_frame = ttk.Frame(self.right_frame)
        form_frame.pack(fill=BOTH, expand=YES)

        # Campo ID (oculto cuando se crea nuevo)
        id_frame = ttk.Frame(form_frame)
        id_frame.pack(fill=X, pady=5)

        ttk.Label(id_frame, text="ID:", width=12).pack(side=LEFT)
        self.id_label = ttk.Label(
            id_frame,
            text="Nuevo",
            font=("Arial", 10, "bold"),
            bootstyle="info"
        )
        self.id_label.pack(side=LEFT)

        # Campo Nombre
        ttk.Label(form_frame, text="Nombre:").pack(anchor=W, pady=(10, 2))
        self.name_var = ttk.StringVar()
        self.name_entry = ttk.Entry(
            form_frame,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.pack(fill=X, pady=(0, 10))

        # Campo Precio
        ttk.Label(form_frame, text="Precio:").pack(anchor=W, pady=(10, 2))
        self.price_var = ttk.StringVar()
        self.price_entry = ttk.Entry(
            form_frame,
            textvariable=self.price_var,
            width=30
        )
        self.price_entry.pack(fill=X, pady=(0, 10))

        # Botones de acción
        btn_container = ttk.Frame(form_frame)
        btn_container.pack(fill=X, pady=(20, 0))

        ttk.Button(
            btn_container,
            text="Nuevo",
            command=self.new_product,
            bootstyle="success",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Guardar",
            command=self.save_product,
            bootstyle="primary",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Eliminar",
            command=self.delete_product,
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


    def new_product(self):
        """Preparar formulario para nuevo producto"""
        self.clear_form()
        self.name_entry.focus()


    def save_product(self):
        """Guardar producto (crear o actualizar)"""
        # Validar campos
        name = self.name_var.get().strip()
        price_str = self.price_var.get().strip()

        if not name:
            messagebox.showerror("Error", "El nombre del producto es obligatorio")
            self.name_entry.focus()
            return

        if not price_str:
            messagebox.showerror("Error", "El precio es obligatorio")
            self.price_entry.focus()
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("El precio no puede ser negativo")
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido")
            self.price_entry.focus()
            return

        # Guardar en base de datos
        if self.selected_product_id is None:
            # Crear nuevo producto
            success, result = self.db.add_product(name, price)
            if success:
                messagebox.showinfo("Éxito", "Producto creado exitosamente")
                self.clear_form()
                # Recargar tabla de productos
                if hasattr(self.parent, 'products_section'):
                    self.parent.products_section.load_products()
            else:
                messagebox.showerror("Error", f"No se pudo crear el producto: {result}")
        else:
            # Actualizar producto existente
            success, result = self.db.update_product(self.selected_product_id, name, price)
            if success:
                messagebox.showinfo("Éxito", "Producto actualizado exitosamente")
                self.clear_form()
                # Recargar tabla de productos
                if hasattr(self.parent, 'products_section'):
                    self.parent.products_section.load_products()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el producto: {result}")


    def delete_product(self):
        """Eliminar producto (desactivar)"""
        if self.selected_product_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return

        # Confirmar eliminación
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el producto '{self.name_var.get()}'?"
        )

        if not confirm:
            return

        # Eliminar en base de datos
        success, result = self.db.delete_product(self.selected_product_id)
        if success:
            messagebox.showinfo("Éxito", "Producto eliminado exitosamente")
            self.clear_form()
            # Recargar tabla de productos
            if hasattr(self.parent, 'products_section'):
                self.parent.products_section.load_products()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {result}")


    def clear_form(self):
        """Limpiar formulario"""
        self.selected_product_id = None
        self.id_label.config(text="Nuevo")
        self.name_var.set("")
        self.price_var.set("")

        # Deseleccionar en tabla
        if hasattr(self.parent, 'products_section'):
            self.parent.products_section.clear_selection()