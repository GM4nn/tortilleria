from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from app.constants import mexico_now
from app.data.providers.supplies import supply_provider


class SuppliesForm(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)

        self.app = app
        self.parent = parent
        self.provider = supply_provider
        self.main_container = main_container
        self.selected_supply_id = None

        self.setup_ui()


    def setup_ui(self):
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.setup_form_section()
        self.setup_btn_actions()


    def setup_form_section(self):

        ttk.Label(
            self.right_frame,
            text="Datos del Insumo",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 15))

        self.form_frame = ttk.Frame(self.right_frame)
        self.form_frame.pack(fill=X)

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

        ttk.Label(self.form_frame, text="Nombre Insumo:*").pack(anchor=W, pady=(10, 2))
        self.name_var = ttk.StringVar()
        self.name_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.pack(fill=X, pady=(0, 5))

        ttk.Label(self.form_frame, text="Proveedor:*").pack(anchor=W, pady=(5, 2))
        self.supplier_var = ttk.StringVar()
        self.supplier_combo = ttk.Combobox(
            self.form_frame,
            textvariable=self.supplier_var,
            state="readonly",
            width=28
        )
        self.supplier_combo.pack(fill=X, pady=(0, 5))
        self.load_suppliers()

        ttk.Label(self.form_frame, text="Cantidad:*").pack(anchor=W, pady=(5, 2))
        self.quantity_var = ttk.StringVar()
        self.quantity_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.quantity_var,
            width=30
        )
        self.quantity_entry.pack(fill=X, pady=(0, 5))
        self.quantity_entry.bind('<KeyRelease>', self.calculate_total)

        ttk.Label(self.form_frame, text="Unidad:*").pack(anchor=W, pady=(5, 2))
        self.unit_var = ttk.StringVar()
        self.unit_combo = ttk.Combobox(
            self.form_frame,
            textvariable=self.unit_var,
            values=["kilos", "litros", "piezas", "costales", "bultos", "cajas"],
            width=28
        )
        self.unit_combo.pack(fill=X, pady=(0, 5))

        ttk.Label(self.form_frame, text="Precio Unitario ($):*").pack(anchor=W, pady=(5, 2))
        self.unit_price_var = ttk.StringVar()
        self.unit_price_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.unit_price_var,
            width=30
        )
        self.unit_price_entry.pack(fill=X, pady=(0, 5))
        self.unit_price_entry.bind('<KeyRelease>', self.calculate_total)

        ttk.Label(self.form_frame, text="Precio Total ($):").pack(anchor=W, pady=(5, 2))
        self.total_var = ttk.StringVar()
        self.total_entry = ttk.Entry(
            self.form_frame,
            textvariable=self.total_var,
            width=30
        )
        self.total_entry.pack(fill=X, pady=(0, 5))

        ttk.Label(self.form_frame, text="Fecha de Compra:").pack(anchor=W, pady=(5, 2))
        self.date_entry = ttk.DateEntry(
            self.form_frame,
            bootstyle="primary",
            width=28
        )
        self.date_entry.pack(fill=X, pady=(0, 5))

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
            command=self.new_supply,
            bootstyle="success",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Guardar",
            command=self.save_supply,
            bootstyle="primary",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_container,
            text="Eliminar",
            command=self.delete_supply,
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


    def load_suppliers(self):

        suppliers = self.provider.get_suppliers_list()
        self.suppliers_dict = {name: id for id, name in suppliers}
        self.supplier_combo['values'] = list(self.suppliers_dict.keys())


    def calculate_total(self, event=None):
        """Calculate total price based on quantity and unit price"""
        try:
            quantity = float(self.quantity_var.get() or 0)
            unit_price = float(self.unit_price_var.get() or 0)
            total = quantity * unit_price
            self.total_var.set(f"{total:.2f}")
        except ValueError:
            pass


    def new_supply(self):
        self.clear_form()
        self.name_entry.focus()


    def save_supply(self):

        name = self.name_var.get().strip()
        supplier_name = self.supplier_var.get()
        quantity = self.quantity_var.get().strip()
        unit = self.unit_var.get().strip()
        unit_price = self.unit_price_var.get().strip()
        total_price = self.total_var.get().strip()
        notes = self.notes_text.get('1.0', 'end-1c').strip()

        if not name:
            messagebox.showerror("Error", "El nombre del insumo es obligatorio")
            self.name_entry.focus()
            return

        if not supplier_name:
            messagebox.showerror("Error", "Debe seleccionar un proveedor")
            return

        if not quantity or not unit_price:
            messagebox.showerror("Error", "La cantidad y precio son obligatorios")
            return

        try:
            quantity = float(quantity)
            unit_price = float(unit_price)
            total_price = float(total_price) if total_price else quantity * unit_price
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precios deben ser números válidos")
            return

        supplier_id = self.suppliers_dict.get(supplier_name)
        purchase_date_str = self.date_entry.entry.get()

        try:
            purchase_date = datetime.strptime(purchase_date_str, "%m/%d/%Y")
        except:
            purchase_date = mexico_now()

        if self.selected_supply_id is None:

            success, result = self.provider.add(
                name, supplier_id, quantity, unit,
                unit_price, total_price, purchase_date, notes
            )

            if success:
                messagebox.showinfo("Éxito", f"Insumo registrado con ID: {result}")
                self.clear_form()

                if hasattr(self.parent, 'table_section'):
                    self.parent.table_section.load_supplies()
            else:
                messagebox.showerror("Error", f"No se pudo crear el insumo: {result}")
        else:

            success, result = self.provider.update(
                self.selected_supply_id, name, supplier_id, quantity, unit,
                unit_price, total_price, purchase_date, notes
            )
            if success:
                messagebox.showinfo("Éxito", "Insumo actualizado exitosamente")
                self.clear_form()

                if hasattr(self.parent, 'table_section'):
                    self.parent.table_section.load_supplies()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el insumo: {result}")


    def delete_supply(self):

        if self.selected_supply_id is None:
            messagebox.showwarning("Advertencia", "Seleccione un insumo para eliminar")
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el insumo '{self.name_var.get()}'?"
        )

        if not confirm:
            return

        success, result = self.provider.delete(self.selected_supply_id)

        if success:
            messagebox.showinfo("Éxito", "Insumo eliminado exitosamente")
            self.clear_form()

            if hasattr(self.parent, 'table_section'):
                self.parent.table_section.load_supplies()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar el insumo: {result}")


    def clear_form(self):

        self.selected_supply_id = None
        self.id_label.config(text="Nuevo")
        self.name_var.set("")
        self.supplier_var.set("")
        self.quantity_var.set("")
        self.unit_var.set("")
        self.unit_price_var.set("")
        self.total_var.set("")
        self.notes_text.delete('1.0', 'end')

        if hasattr(self.parent, 'table_section'):
            self.parent.table_section.clear_selection()


    def load_supply(self, supply_data):
        """Load supply data into form for editing"""
        
        self.selected_supply_id = supply_data['id']
        self.id_label.config(text=str(supply_data['id']))
        self.name_var.set(supply_data['supply_name'])
        self.supplier_var.set(supply_data['supplier_name'])
        self.quantity_var.set(str(supply_data['quantity']))
        self.unit_var.set(supply_data['unit'])
        self.unit_price_var.set(str(supply_data['unit_price']))
        self.total_var.set(str(supply_data['total_price']))
        self.notes_text.delete('1.0', 'end')
        
        if supply_data.get('notes'):
            self.notes_text.insert('1.0', supply_data['notes'])
