import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from app.data.providers.supplies import supply_provider
from app.constants import SUPPLY_UNITS


class SupplyForm(ttk.Frame):
    """Formulario simplificado para crear/editar insumos"""

    def __init__(self, parent, app, on_close_callback):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = supply_provider
        self.on_close_callback = on_close_callback
        self.selected_supply_id = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the form UI"""

        
        self.title_label = ttk.Label(
            self,
            text="Nuevo Insumo",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=(0, 20))

        # Formulario
        form_container = ttk.Frame(self)
        form_container.pack(fill=BOTH, expand=YES, padx=10)
        
        self.setup_gui_form(form_container)
        self.setup_gui_actions_buttons(form_container)

    def setup_gui_form(self, form_container):

        # ID (solo lectura, se muestra al editar)
        self.id_frame = ttk.Frame(form_container)
        self.id_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(self.id_frame, text="ID:", width=12).pack(side=LEFT)
        self.id_label = ttk.Label(
            self.id_frame,
            text="Nuevo",
            font=("Arial", 10, "bold"),
            bootstyle="info"
        )
        self.id_label.pack(side=LEFT)

        # Nombre del insumo
        ttk.Label(form_container, text="Nombre del Insumo:*").pack(anchor=W, pady=(10, 2))
        self.name_var = ttk.StringVar()
        self.name_entry = ttk.Entry(
            form_container,
            textvariable=self.name_var,
            width=30
        )
        self.name_entry.pack(fill=X, pady=(0, 10))

        # Proveedor principal
        ttk.Label(form_container, text="Proveedor Principal:*").pack(anchor=W, pady=(5, 2))
        self.supplier_var = ttk.StringVar()
        self.supplier_combo = ttk.Combobox(
            form_container,
            textvariable=self.supplier_var,
            state="readonly",
            width=28
        )
        self.supplier_combo.pack(fill=X, pady=(0, 10))
        self.load_suppliers()

        # Unidad de medida
        ttk.Label(form_container, text="Unidad de Medida:*").pack(anchor=W, pady=(5, 2))
        self.unit_var = ttk.StringVar()
        self.unit_combo = ttk.Combobox(
            form_container,
            textvariable=self.unit_var,
            state="readonly",
            values=SUPPLY_UNITS,
            width=28
        )
        self.unit_combo.pack(fill=X, pady=(0, 10))
        self.unit_combo.current(0)

    def setup_gui_actions_buttons(self, form_container):
        # Nota informativa
        info_frame = ttk.Frame(form_container)
        info_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(
            info_frame,
            text="Nota: Despu\u00e9s de crear el insumo, podr\u00e1s registrar compras desde su detalle.",
            font=("Arial", 9),
            bootstyle="info",
            wraplength=220
        ).pack(anchor=W)

        # Botones
        btn_frame = ttk.Frame(form_container)
        btn_frame.pack(fill=X, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Nuevo",
            command=self.new_supply,
            bootstyle="success",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_frame,
            text="Guardar",
            command=self.save_supply,
            bootstyle="primary",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_frame,
            text="Eliminar",
            command=self.delete_supply,
            bootstyle="danger",
            width=20
        ).pack(fill=X, pady=5)

        ttk.Button(
            btn_frame,
            text="Limpiar",
            command=self.clear_form,
            bootstyle="secondary-outline",
            width=20
        ).pack(fill=X, pady=5)

    def load_suppliers(self):
        """Load suppliers list"""
        suppliers = self.provider.get_suppliers_list()
        self.suppliers_dict = {name: id for id, name in suppliers}
        self.supplier_combo['values'] = list(self.suppliers_dict.keys())

    def save_supply(self):
        """Save the supply"""
        name = self.name_var.get().strip()
        supplier_name = self.supplier_var.get()

        if not name:
            Messagebox.show_error("El nombre del insumo es obligatorio", "Error")
            self.name_entry.focus()
            return

        if not supplier_name:
            Messagebox.show_error("Debe seleccionar un proveedor", "Error")
            return

        unit = self.unit_var.get()
        if not unit:
            Messagebox.show_error("Debe seleccionar una unidad de medida", "Error")
            return

        supplier_id = self.suppliers_dict.get(supplier_name)

        if self.selected_supply_id is None:
            # Crear nuevo insumo
            success, result = self.provider.create_supply(name, supplier_id, unit)

            if success:
                Messagebox.show_info(f"Insumo creado con ID: {result}", "\u00c9xito")
                self.clear_form()
                if self.on_close_callback:
                    self.on_close_callback()
            else:
                Messagebox.show_error(f"No se pudo crear el insumo: {result}", "Error")
        else:
            # Actualizar insumo existente
            success, result = self.provider.update_supply(
                self.selected_supply_id, name, supplier_id, unit
            )

            if success:
                Messagebox.show_info("Insumo actualizado exitosamente", "\u00c9xito")
                self.clear_form()
                if self.on_close_callback:
                    self.on_close_callback()
            else:
                Messagebox.show_error(f"No se pudo actualizar el insumo: {result}", "Error")

    def new_supply(self):
        """Limpiar formulario y enfocar nombre"""
        self.clear_form()
        self.name_entry.focus()

    def delete_supply(self):
        """Eliminar el insumo seleccionado"""
        if self.selected_supply_id is None:
            Messagebox.show_warning("Seleccione un insumo para eliminar", "Advertencia")
            return

        confirm = Messagebox.yesno(
            f"¿Está seguro que desea eliminar el insumo '{self.name_var.get()}'?",
            "Confirmar eliminación"
        )
        if not confirm:
            return

        success, result = self.provider.delete_supply(self.selected_supply_id)
        if success:
            Messagebox.show_info("Insumo eliminado exitosamente", "Éxito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"No se pudo eliminar el insumo: {result}", "Error")

    def load_supply(self, supply_data):
        """Load supply data for editing"""
        self.selected_supply_id = supply_data['id']
        self.id_label.configure(text=str(supply_data['id']))
        self.title_label.configure(text="Editar Insumo")
        self.name_var.set(supply_data['supply_name'])
        self.supplier_var.set(supply_data['supplier_name'])
        self.unit_var.set(supply_data.get('unit', 'kilos'))

    def clear_form(self):
        """Clear the form"""
        self.selected_supply_id = None
        self.id_label.configure(text="Nuevo")
        self.title_label.configure(text="Nuevo Insumo")
        self.name_var.set("")
        self.supplier_var.set("")
        self.unit_combo.current(0)
