import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.supplies.supplies_grid import SuppliesGrid
from app.gui.supplies.supply_detail import SupplyDetailView
from app.gui.supplies.supply_form import SupplyForm
from app.gui.supplies.purchase_form import PurchaseForm


class SuppliesContent(ttk.Frame):
    """Contenedor principal del m\u00f3dulo de insumos"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_view = None

        self.setup_ui()
        self.show_grid_view()

    def setup_ui(self):
        """Setup the main container"""
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def clear_view(self):
        """Clear the current view"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_grid_view(self):
        """Show the grid view with supply cards"""
        self.clear_view()

        # Grid a la izquierda
        self.grid_view = SuppliesGrid(
            self.main_container,
            self.app,
            on_card_click=self.show_detail_view,
            on_new_supply=self.show_supply_form
        )
        self.grid_view.pack(fill=BOTH, expand=YES)

        self.current_view = "grid"

    def show_detail_view(self, supply_id):
        """Show the detail view for a specific supply"""
        self.clear_view()

        self.detail_view = SupplyDetailView(
            self.main_container,
            self.app,
            supply_id,
            on_back_callback=self.show_grid_view,
            on_new_purchase_callback=self.show_purchase_form
        )
        self.detail_view.pack(fill=BOTH, expand=YES)

        self.current_view = "detail"

    def show_supply_form(self):
        """Show the form to create a new supply"""
        self.clear_view()

        # Dividir la pantalla: grid a la izquierda, formulario a la derecha
        # Grid (mantener visible)
        left_frame = ttk.Frame(self.main_container)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.grid_view = SuppliesGrid(
            left_frame,
            self.app,
            on_card_click=self.show_detail_view,
            on_new_supply=self.show_supply_form
        )
        self.grid_view.pack(fill=BOTH, expand=YES)

        # Formulario a la derecha
        right_frame = ttk.Frame(self.main_container)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.supply_form = SupplyForm(
            right_frame,
            self.app,
            on_close_callback=self.show_grid_view
        )
        self.supply_form.pack(fill=BOTH, expand=YES)

        self.current_view = "form"

    def show_purchase_form(self, supply_id, supply_name):
        """Show the form to register a new purchase"""
        # Obtener el proveedor sugerido del insumo
        from app.data.providers.supplies import supply_provider
        supply_data = supply_provider.get_supply_by_id(supply_id)
        suggested_supplier_id = supply_data['supplier_id'] if supply_data else None

        # Si estamos en la vista de detalle, mostrar formulario a la derecha
        if self.current_view == "detail":
            # Crear un nuevo layout con detalle a la izquierda y formulario a la derecha
            self.clear_view()

            # Detalle a la izquierda (reducido)
            left_frame = ttk.Frame(self.main_container)
            left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

            self.detail_view = SupplyDetailView(
                left_frame,
                self.app,
                supply_id,
                on_back_callback=self.show_grid_view,
                on_new_purchase_callback=lambda sid, sname: None,  # Deshabilitar mientras está el formulario
                on_purchase_selected_callback=lambda: self.show_detail_view(supply_id)  # Cerrar formulario al seleccionar renglón
            )
            self.detail_view.pack(fill=BOTH, expand=YES)

            # Formulario a la derecha
            right_frame = ttk.Frame(self.main_container)
            right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

            self.purchase_form = PurchaseForm(
                right_frame,
                self.app,
                on_close_callback=lambda: self.show_detail_view(supply_id)
            )
            self.purchase_form.pack(fill=BOTH, expand=YES)
            self.purchase_form.set_supply(supply_id, supply_name, suggested_supplier_id)

            self.current_view = "purchase"
