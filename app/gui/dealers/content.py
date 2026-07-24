"""
Modulo de Repartidores - panel de tabla (izquierda) y formulario (derecha).
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from app.gui.dealers.dealers_form import DealersForm
from app.gui.dealers.dealers_table import DealersTable


class DealersContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.setup_ui()

    def setup_ui(self):

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.table_section = DealersTable(self, self.app, self.main_container)
        self.table_section.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)

        self.form_section = DealersForm(self, self.app, self.main_container)
        self.form_section.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10, pady=10)
