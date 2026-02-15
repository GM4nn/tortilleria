import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.supplies.supplies_grid import SuppliesGrid
from app.gui.supplies.supply_detail import SupplyDetailView
from app.gui.supplies.supply_form import SupplyForm
from app.gui.supplies.purchase_form import PurchaseForm


class SuppliesContent(ttk.Frame):
    """Contenedor principal del módulo de insumos"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_view = None
        self._transitioning = False
        self._current_supply_id = None

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

        self.grid_view = SuppliesGrid(
            self.main_container,
            self.app,
            on_card_click=self.show_detail_view,
            on_new_supply=self.show_supply_form
        )
        self.grid_view.pack(fill=BOTH, expand=YES)

        self.current_view = "grid"

    def show_detail_view(self, supply_id):
        """Show the detail view with purchase form sidebar"""
        self.clear_view()
        self._current_supply_id = supply_id

        # Obtener proveedor sugerido
        from app.data.providers.supplies import supply_provider
        supply_data = supply_provider.get_supply_by_id(supply_id)
        suggested_supplier_id = supply_data['supplier_id'] if supply_data else None
        supply_name = supply_data['supply_name'] if supply_data else ""

        # Left: Detail view
        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))

        self.detail_view = SupplyDetailView(
            self.left_frame,
            self.app,
            supply_id,
            on_back_callback=self.show_grid_view,
            on_edit_purchase_callback=self._on_purchase_selected,
            on_tab_change_callback=self._on_tab_change
        )
        self.detail_view.pack(fill=BOTH, expand=YES)

        # Right: Purchase form sidebar (siempre visible en tab historial)
        self.right_frame = ttk.Frame(self.main_container, width=400)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(5, 0))

        self.purchase_form = PurchaseForm(
            self.right_frame,
            self.app,
            on_close_callback=self._on_form_saved
        )
        self.purchase_form.pack(fill=BOTH, expand=YES)
        self.purchase_form.set_supply(supply_id, supply_name, suggested_supplier_id)

        self.current_view = "detail"

    def _on_purchase_selected(self, supply_id, supply_name, purchase_data):
        """When a purchase row is clicked, switch form to edit mode"""
        if hasattr(self, 'purchase_form') and self.purchase_form.winfo_exists():
            self.purchase_form.clear_form()
            self.purchase_form.set_edit_mode(supply_id, supply_name, purchase_data)

    def _on_form_saved(self):
        """After save or cancel, reset form to new mode and refresh detail"""
        if not self._current_supply_id:
            return

        from app.data.providers.supplies import supply_provider
        supply_data = supply_provider.get_supply_by_id(self._current_supply_id)
        suggested_supplier_id = supply_data['supplier_id'] if supply_data else None
        supply_name = supply_data['supply_name'] if supply_data else ""

        # Refresh detail view data
        if hasattr(self, 'detail_view') and self.detail_view.winfo_exists():
            self.detail_view.refresh()

        # Reset form to new purchase mode
        if hasattr(self, 'purchase_form') and self.purchase_form.winfo_exists():
            self.purchase_form.clear_form()
            self.purchase_form.set_supply(self._current_supply_id, supply_name, suggested_supplier_id)

    def _on_tab_change(self, tab_name):
        """Show/hide sidebar based on active tab"""
        if tab_name == "historial":
            # Mostrar sidebar
            if hasattr(self, 'right_frame') and self.right_frame.winfo_exists():
                self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(5, 0))
                # Reset form to new mode
                self._reset_form_to_new()
        else:
            # Ocultar sidebar en tab períodos
            if hasattr(self, 'right_frame') and self.right_frame.winfo_exists():
                self.right_frame.pack_forget()

    def _reset_form_to_new(self):
        """Reset form to new purchase mode"""
        if not self._current_supply_id:
            return

        from app.data.providers.supplies import supply_provider
        supply_data = supply_provider.get_supply_by_id(self._current_supply_id)
        suggested_supplier_id = supply_data['supplier_id'] if supply_data else None
        supply_name = supply_data['supply_name'] if supply_data else ""

        if hasattr(self, 'purchase_form') and self.purchase_form.winfo_exists():
            self.purchase_form.clear_form()
            self.purchase_form.set_supply(self._current_supply_id, supply_name, suggested_supplier_id)

    def show_supply_form(self):
        """Show the form to create a new supply"""
        self.clear_view()

        left_frame = ttk.Frame(self.main_container)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.grid_view = SuppliesGrid(
            left_frame,
            self.app,
            on_card_click=self.show_detail_view,
            on_new_supply=self.show_supply_form
        )
        self.grid_view.pack(fill=BOTH, expand=YES)

        right_frame = ttk.Frame(self.main_container)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.supply_form = SupplyForm(
            right_frame,
            self.app,
            on_close_callback=self.show_grid_view
        )
        self.supply_form.pack(fill=BOTH, expand=YES)

        self.current_view = "form"
