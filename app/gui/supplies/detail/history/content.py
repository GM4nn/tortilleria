import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.supplies.detail.history.historic_table import HistoricTable
from app.gui.supplies.detail.history.purchase_form.content import PurchaseForm


class HistoryContent:
    """Coordinador del tab historial: tabla de compras + formulario sidebar"""

    def __init__(self, table_parent, form_parent, app, supply_data, on_form_saved=None):
        self.app = app
        self.supply_data = supply_data
        self.on_form_saved = on_form_saved

        # Tabla de compras (lado izquierdo) - paginacion server-side
        self.table = HistoricTable(
            table_parent,
            supply_data['id'],
            on_row_click=self._on_purchase_selected
        )
        self.table.pack(fill=BOTH, expand=YES)

        # Formulario de compra (sidebar derecho)
        self.form = PurchaseForm(
            form_parent,
            app,
            on_close_callback=self._on_form_closed
        )
        self.form.pack(fill=BOTH, expand=YES)
        self.form.set_supply(
            supply_data['id'],
            supply_data['supply_name'],
            supply_data.get('supplier_id')
        )

    def _on_purchase_selected(self, supply_id, supply_name, purchase_data):
        """Al hacer click en una fila, cargar en el form para editar"""
        self.form.clear_form()
        self.form.set_edit_mode(supply_id, self.supply_data['supply_name'], purchase_data)

    def _on_form_closed(self):
        """Al guardar/cancelar, refrescar tabla y resetear form"""
        if self.on_form_saved:
            self.on_form_saved()

    def refresh(self, supply_data):
        self.supply_data = supply_data
        self.table.refresh()

    def reset_form(self):
        """Resetear form a modo nueva compra"""
        self.form.clear_form()
        self.form.set_supply(
            self.supply_data['id'],
            self.supply_data['supply_name'],
            self.supply_data.get('supplier_id')
        )
