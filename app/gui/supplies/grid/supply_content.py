import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.supplies.grid.supply_grid import SupplyGrid
from app.gui.supplies.grid.supply_form import SupplyForm


class SupplyContent(ttk.Frame):
    """Contenedor de la vista de grid de insumos con formulario siempre visible"""

    def __init__(self, parent, app, on_card_click):
        super().__init__(parent)
        self.app = app
        self.on_card_click = on_card_click

        self.setup_ui()

    def setup_ui(self):

        left_frame = ttk.Frame(self)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.grid_view = SupplyGrid(
            left_frame,
            self.app,
            on_card_click=self.on_card_click,
            on_edit_supply=self.on_edit_supply
        )
        self.grid_view.pack(fill=BOTH, expand=YES)

        right_frame = ttk.Frame(self, width=250)
        right_frame.pack_propagate(False)
        right_frame.pack(side=RIGHT, fill=BOTH, padx=(10, 0))

        self.supply_form = SupplyForm(
            right_frame,
            self.app,
            on_close_callback=self.on_form_saved
        )
        self.supply_form.pack(fill=BOTH, expand=YES)

    def on_edit_supply(self, supply_data):
        """Cargar datos del insumo en el formulario para editar"""
        self.supply_form.load_supply(supply_data)

    def on_form_saved(self):
        """Refrescar grid al guardar/cancelar"""
        self.grid_view.load_supplies()
