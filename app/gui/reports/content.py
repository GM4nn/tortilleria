"""
Módulo de Reportes
Análisis detallado de ventas, clientes, insumos y proveedores
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .sales.sales_content import SalesTab
from .customers.customers_content import CustomersTab
from .supplies.supplies_content import SuppliesTab
from .suppliers.suppliers_content import SuppliersTab


class ReportsContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Configure custom styles
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        """Configure custom styles for the reports module"""
        style = ttk.Style()

        # Configure larger font for section titles (Labelframe)
        style.configure('primary.TLabelframe.Label', font=('Segoe UI', 14, 'bold'))
        style.configure('info.TLabelframe.Label', font=('Segoe UI', 14, 'bold'))
        style.configure('warning.TLabelframe.Label', font=('Segoe UI', 14, 'bold'))
        style.configure('success.TLabelframe.Label', font=('Segoe UI', 14, 'bold'))
        style.configure('danger.TLabelframe.Label', font=('Segoe UI', 14, 'bold'))

    def setup_ui(self):
        # Title section
        title_frame = ttk.Frame(self, padding=20)
        title_frame.pack(fill=X)

        ttk.Label(
            title_frame,
            text="Módulo de Reportes",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor=W)

        ttk.Label(
            title_frame,
            text="Análisis detallado de ventas, clientes, insumos y proveedores",
            font=("Segoe UI", 11),
            foreground="#6c757d"
        ).pack(anchor=W, pady=(5, 0))

        # Tabs container
        tabs_container = ttk.Frame(self, padding=(20, 0, 20, 20))
        tabs_container.pack(fill=BOTH, expand=YES)

        # Create tab buttons frame
        tab_buttons_frame = ttk.Frame(tabs_container)
        tab_buttons_frame.pack(fill=X, pady=(0, 20))

        # Tab buttons
        self.tab_buttons = {}
        tabs_config = [
            ("ventas", "🛒 Ventas", "primary"),
            ("clientes", "👥 Clientes", "info"),
            ("insumos", "📦 Insumos", "warning"),
            ("proveedores", "🏢 Proveedores", "success")
        ]

        for tab_id, label, bootstyle in tabs_config:
            btn = ttk.Button(
                tab_buttons_frame,
                text=label,
                bootstyle=f"outline-{bootstyle}",
                command=lambda t=tab_id: self.switch_tab(t)
            )
            btn.pack(side=LEFT, fill=X, expand=True, padx=5)
            self.tab_buttons[tab_id] = btn

        # Tab content frame
        self.tab_content = ttk.Frame(tabs_container)
        self.tab_content.pack(fill=BOTH, expand=YES)

        # Create tabs
        self.tabs = {
            "ventas": SalesTab(self.tab_content, self.app),
            "clientes": CustomersTab(self.tab_content, self.app),
            "insumos": SuppliesTab(self.tab_content, self.app),
            "proveedores": SuppliersTab(self.tab_content, self.app)
        }

        # Show first tab
        self.current_tab = None
        self.switch_tab("ventas")

    def switch_tab(self, tab_id):
        """Switch between tabs"""
        if self.current_tab == tab_id:
            return

        # Hide current tab
        if self.current_tab:
            self.tabs[self.current_tab].pack_forget()
            # Reset button style
            for tid, btn in self.tab_buttons.items():
                bootstyle = "primary" if tid == "ventas" else "info" if tid == "clientes" else "warning" if tid == "insumos" else "success"
                btn.config(bootstyle=f"outline-{bootstyle}")

        # Show new tab
        self.tabs[tab_id].pack(fill=BOTH, expand=YES)
        self.current_tab = tab_id

        # Update button style
        bootstyle = "primary" if tab_id == "ventas" else "info" if tab_id == "clientes" else "warning" if tab_id == "insumos" else "success"
        self.tab_buttons[tab_id].config(bootstyle=bootstyle)

        # Refresh tab data
        self.tabs[tab_id].refresh_data()
