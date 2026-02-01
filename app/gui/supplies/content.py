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
        self._transitioning = False  # Flag para evitar transiciones duplicadas

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
            on_new_purchase_callback=self.show_purchase_form,
            on_edit_purchase_callback=self.show_edit_purchase_form
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
                on_edit_purchase_callback=lambda sid, sname, pdata: self.show_detail_view(supply_id)  # Cerrar formulario al hacer doble clic
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

    def show_edit_purchase_form(self, supply_id, supply_name, purchase_data):
        """Show the form to edit an existing purchase"""
        # Evitar transiciones duplicadas
        if self._transitioning:
            return

        # Si ya estamos en modo edición, solo actualizar el formulario existente
        if self.current_view == "edit_purchase" and hasattr(self, 'purchase_form') and self.purchase_form.winfo_exists():
            self.purchase_form.clear_form()
            self.purchase_form.set_edit_mode(supply_id, supply_name, purchase_data)
            return

        # Guardar el supply_id actual para usarlo en callbacks
        self._current_supply_id = supply_id

        # Si estamos en la vista de detalle, solo agregar el formulario a la derecha sin recrear todo
        if self.current_view == "detail" and hasattr(self, 'detail_view') and self.detail_view.winfo_exists():
            self._transitioning = True  # Bloquear transiciones durante el proceso

            # Actualizar los callbacks del detail_view existente
            self.detail_view.on_edit_purchase_callback = self._update_edit_form
            self.detail_view.on_tab_change_callback = self._on_tab_change
            self.detail_view.on_new_purchase_callback = lambda sid, sname: None

            # Reconfigurar el detail_view para que no ocupe todo el ancho
            self.detail_view.pack_configure(side=LEFT, padx=(0, 10))

            # Crear formulario a la derecha
            self.right_frame = ttk.Frame(self.main_container, width=400)
            self.right_frame.pack_propagate(False)  # Mantener el ancho fijo
            self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

            self.purchase_form = PurchaseForm(
                self.right_frame,
                self.app,
                on_close_callback=self._close_edit_form
            )
            self.purchase_form.pack(fill=BOTH, expand=YES)
            self.purchase_form.set_edit_mode(supply_id, supply_name, purchase_data)

            self.current_view = "edit_purchase"

            # Desbloquear después de un pequeño delay para que el UI se estabilice
            self.after(100, self._end_transition)
            return

        # Fallback: crear todo desde cero
        self.clear_view()

        # Detalle a la izquierda
        left_frame = ttk.Frame(self.main_container)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.detail_view = SupplyDetailView(
            left_frame,
            self.app,
            supply_id,
            on_back_callback=self.show_grid_view,
            on_new_purchase_callback=lambda sid, sname: None,
            on_edit_purchase_callback=self._update_edit_form,
            on_tab_change_callback=self._on_tab_change
        )
        self.detail_view.pack(fill=BOTH, expand=YES)

        # Formulario a la derecha (modo edición)
        self.right_frame = ttk.Frame(self.main_container)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.purchase_form = PurchaseForm(
            self.right_frame,
            self.app,
            on_close_callback=self._close_edit_form
        )
        self.purchase_form.pack(fill=BOTH, expand=YES)
        self.purchase_form.set_edit_mode(supply_id, supply_name, purchase_data)

        self.current_view = "edit_purchase"

    def _update_edit_form(self, supply_id, supply_name, purchase_data):
        """Update the edit form with new purchase data (when selecting another row)"""
        if hasattr(self, 'purchase_form') and self.purchase_form.winfo_exists():
            self.purchase_form.clear_form()
            self.purchase_form.set_edit_mode(supply_id, supply_name, purchase_data)

    def _close_edit_form(self):
        """Close the edit form panel without recreating the detail view"""
        # Evitar cerrar si estamos en transición o no estamos en modo edición
        if self._transitioning or self.current_view != "edit_purchase":
            return

        if hasattr(self, 'right_frame') and self.right_frame.winfo_exists():
            self.right_frame.destroy()

        if hasattr(self, 'detail_view') and self.detail_view.winfo_exists():
            # Restaurar el pack del detail_view para que ocupe todo el ancho
            self.detail_view.pack_configure(side=LEFT, fill=BOTH, expand=YES, padx=0)
            # Restaurar callbacks originales
            self.detail_view.on_edit_purchase_callback = self.show_edit_purchase_form
            self.detail_view.on_new_purchase_callback = self.show_purchase_form
            self.detail_view.on_tab_change_callback = None
            # Deseleccionar el renglón de la tabla
            if hasattr(self.detail_view, 'purchases_table'):
                self.detail_view.purchases_table.view.selection_remove(
                    self.detail_view.purchases_table.view.selection()
                )

        self.current_view = "detail"

    def _end_transition(self):
        """End the transition state"""
        self._transitioning = False

    def _on_tab_change(self, tab_name):
        """Handle tab change - close edit form when switching to Periodos"""
        if tab_name == "periodos":
            self._close_edit_form()
