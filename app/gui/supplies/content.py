import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.supplies.grid.supply_content import SupplyContent
from app.gui.supplies.detail.supply_detail import SupplyDetailView


class SuppliesContent(ttk.Frame):
    """Contenedor principal del módulo de insumos: grid ↔ detail"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_view = None

        self.setup_ui()
        self.show_grid_view()

    def setup_ui(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def clear_view(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_grid_view(self):
        self.clear_view()

        self.supply_content = SupplyContent(
            self.main_container,
            self.app,
            on_card_click=self.show_detail_view
        )
        self.supply_content.pack(fill=BOTH, expand=YES)

        self.current_view = "grid"

    def show_detail_view(self, supply_id):
        self.clear_view()

        self.detail_view = SupplyDetailView(
            self.main_container,
            self.app,
            supply_id,
            on_back_callback=self.show_grid_view
        )
        self.detail_view.pack(fill=BOTH, expand=YES)

        self.current_view = "detail"
