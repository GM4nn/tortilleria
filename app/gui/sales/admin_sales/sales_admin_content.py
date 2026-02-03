import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.sales.admin_sales.sales.sales_list import SalesList
from app.gui.sales.admin_sales.orders.orders_list import OrdersList


class SalesAdminContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.setup_ui()

    def setup_ui(self):
        # Crear Notebook (tabs)
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Tab 1: Ver Ventas
        self.tab_ventas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ventas, text="  💰 Ver Ventas  ")
        self.setup_ventas_tab()

        # Tab 2: Ver Pedidos
        self.tab_pedidos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pedidos, text="  📄 Ver Pedidos  ")
        self.setup_pedidos_tab()

    def setup_ventas_tab(self):
        """Configurar tab de Ver Ventas"""
        self.sales_list = SalesList(self.tab_ventas, self.app, self)
        self.sales_list.pack(fill=BOTH, expand=YES)

    def setup_pedidos_tab(self):
        """Configurar tab de Ver Pedidos"""
        self.orders_list = OrdersList(self.tab_pedidos, self.app, self)
        self.orders_list.pack(fill=BOTH, expand=YES)
