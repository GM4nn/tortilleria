"""
Módulo de Navegación - Panel izquierdo con botones
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.home.content import HomeContent
from app.gui.inventory.content import InventoryContent
from app.gui.reports.content import ReportsContent
from app.gui.sales.content import SalesContent


class Navigation(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, width=200, bootstyle="dark")
        self.app = app
        self.setup_ui()


    def setup_ui(self):
        """Configurar interfaz de navegación"""
        
        self.title()
        self.buttons_navigation()


    def title(self):

        header = ttk.Label(
            self,
            text="TORTILLERÍA",
            font=("Arial", 16, "bold"),
            bootstyle="inverse-dark",
            padding=(30, 0)
        )
        header.pack(pady=20)
        
        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=20, pady=0)


    def buttons_navigation(self):

        self.btn_products = ttk.Button(
            self,
            text="📦 Productos",
            command=lambda: self.change_view("products"),
            bootstyle="primary",
            width=18
        )

        self.btn_products.pack(pady=(20,10), padx=10, ipady=10)
        
        self.btn_sales = ttk.Button(
            self,
            text="💰 Ventas",
            command=lambda: self.change_view("sales"),
            bootstyle="success",
            width=18
        )
        self.btn_sales.pack(pady=10, padx=10, ipady=10)
        
        self.btn_reports = ttk.Button(
            self,
            text="📊 Reportes",
            command=lambda: self.change_view("reports"),
            bootstyle="info",
            width=18
        )
        self.btn_reports.pack(pady=10, padx=10, ipady=10)
        
        self.btn_inventory = ttk.Button(
            self,
            text="📦 Inventario",
            command=lambda: self.change_view("inventory"),
            bootstyle="secondary",
            width=18
        )
        self.btn_inventory.pack(pady=10, padx=10, ipady=10)


    def change_view(self, vista):
        """Cambiar la vista del panel central"""

        # Destroy content if prev exists
        if self.app.content:
            self.app.content.destroy()

        if vista == "products":
            self.app.content = HomeContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "sales":            
            self.app.content = SalesContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "reports":
            self.app.content = ReportsContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "inventory":
            self.app.content = InventoryContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)