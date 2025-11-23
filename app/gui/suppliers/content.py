"""
Módulo de Contenido - Contiene panel central y panel derecho
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.suppliers.suppliers_form import SuppliersForm
from app.gui.suppliers.suppliers_table import SuppliersTable


class SuppliersContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.setup_ui()

    def setup_ui(self):

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.table_section = SuppliersTable(self, self.app, self.main_container)
        self.table_section.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)

        self.form_section = SuppliersForm(self, self.app, self.main_container)
        self.form_section.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10, pady=10)