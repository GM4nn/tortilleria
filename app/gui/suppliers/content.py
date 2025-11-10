"""
Módulo de Contenido - Contiene panel central y panel derecho
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class SuppliersContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.setup_ui()
    
    def setup_ui(self):        
        # Mensaje temporal
        ttk.Label(
            self,
            text="Proveedores en desarrollo...",
            font=("Arial", 14)
        ).pack(pady=50)