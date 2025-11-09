

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.inventory.form import FormInventory
from app.gui.inventory.products import ProductsInventory


class InventoryContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.db = app.db

        self.setup_ui()

    def setup_ui(self):

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.products_section = ProductsInventory(self, self.app, self.main_container)
        self.products_section.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)

        self.form_section = FormInventory(self, self.app, self.main_container)
        self.form_section.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10, pady=10)
