"""
Módulo de Contenido - Contiene panel central y panel derecho
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.customers.customers_form import CustomersForm
from app.gui.customers.customers_table import CustomersTable


class CustomersContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.setup_ui()

    def setup_ui(self):

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.table_section = CustomersTable(self, self.app, self.main_container)
        self.table_section.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)

        self.form_section = CustomersForm(self, self.app, self.main_container)
        self.form_section.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10, pady=10)