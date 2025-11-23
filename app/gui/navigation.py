"""
Módulo de Navegación - Panel izquierdo con botones
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from app.gui.customers.content import CustomersContent
from app.gui.inventory.content import InventoryContent
from app.gui.reports.content import ReportsContent
from app.gui.sales.content import SalesContent
from app.gui.suppliers.content import SuppliersContent
from app.gui.supplies.content import SuppliesContent


class Navigation(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, width=200, bootstyle="dark")
        self.app = app
        self.setup_ui()


    def setup_ui(self):
        
        self.title()
        self.buttons_navigation()


    def title(self):

        # Container for logo and text
        header_frame = ttk.Frame(self, bootstyle="dark")
        header_frame.pack(pady=20)

        # Load and resize logo
        logo_image = Image.open("tortilleria_logo.png")
        logo_image = logo_image.resize((40, 40))
        self.logo = ImageTk.PhotoImage(logo_image)

        # Logo label
        logo_label = ttk.Label(
            header_frame,
            image=self.logo,
            bootstyle="inverse-dark"
        )
        logo_label.pack(side=LEFT, padx=(10, 5))

        # Text label
        header = ttk.Label(
            header_frame,
            text="Tierra del Campo",
            font=("Arial", 14, "bold"),
            bootstyle="inverse-dark"
        )
        header.pack(side=LEFT, padx=(0, 10))

        ttk.Separator(self, orient=HORIZONTAL).pack(fill=X, padx=20, pady=0)


    def buttons_navigation(self):
        
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
        
        self.btn_customers = ttk.Button(
            self,
            text="👥 Clientes",
            command=lambda: self.change_view("customers"),
            bootstyle="danger",
            width=18
        )
        self.btn_customers.pack(pady=10, padx=10, ipady=10)

        self.btn_suppliers = ttk.Button(
            self,
            text="🚚 Proveedores",
            command=lambda: self.change_view("suppliers"),
            bootstyle="warning",
            width=18
        )
        self.btn_suppliers.pack(pady=10, padx=10, ipady=10)

        self.btn_supplies = ttk.Button(
            self,
            text="🌽 Insumos",
            command=lambda: self.change_view("supplies"),
            bootstyle="primary",
            width=18
        )
        self.btn_supplies.pack(pady=10, padx=10, ipady=10)


    def change_view(self, vista):
        """Cambiar la vista del panel central"""

        # Destroy content if prev exists
        if self.app.content:
            self.app.content.destroy()

        if vista == "sales":            
            self.app.content = SalesContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "reports":
            self.app.content = ReportsContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "inventory":
            self.app.content = InventoryContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "customers":
            print("clientes")
            self.app.content = CustomersContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "suppliers":
            print("proveedores")
            self.app.content = SuppliersContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)
        elif vista == "supplies":
            print("insumos")
            self.app.content = SuppliesContent(self.app.content_container, self.app)
            self.app.content.pack(fill=BOTH, expand=YES)