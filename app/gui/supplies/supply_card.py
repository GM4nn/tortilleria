import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class SupplyCard(ttk.Frame):
    """Componente de tarjeta para mostrar un insumo"""

    def __init__(self, parent, supply_data, on_click_callback):
        super().__init__(parent, bootstyle="light")
        self.supply_data = supply_data
        self.on_click_callback = on_click_callback

        self.setup_ui()
        self.bind_click_events()

    def setup_ui(self):
        """Setup the card UI"""
        # Container con padding
        container = ttk.Frame(self, padding=15)
        container.pack(fill=BOTH, expand=YES)

        # Nombre del insumo (grande y bold)
        name_label = ttk.Label(
            container,
            text=self.supply_data['supply_name'],
            font=("Arial", 14, "bold"),
            bootstyle="primary"
        )
        name_label.pack(anchor=W, pady=(0, 5))

        # Proveedor
        supplier_frame = ttk.Frame(container)
        supplier_frame.pack(fill=X, pady=2)

        ttk.Label(
            supplier_frame,
            text="Proveedor: ",
            font=("Arial", 9)
        ).pack(side=LEFT)

        ttk.Label(
            supplier_frame,
            text=self.supply_data['supplier_name'],
            font=("Arial", 9, "bold"),
            bootstyle="info"
        ).pack(side=LEFT)

        # Separador
        separator = ttk.Separator(container, orient=HORIZONTAL)
        separator.pack(fill=X, pady=10)

        # Bot\u00f3n para ver detalles
        btn = ttk.Button(
            container,
            text="Ver Detalles",
            command=self._on_click,
            bootstyle="primary-outline",
            width=15
        )
        btn.pack(anchor=E)

        # Configurar el borde del frame principal
        self.configure(relief=RAISED, borderwidth=1)

    def bind_click_events(self):
        """Bind click events to all widgets for card interactivity"""
        def on_enter(e):
            self.configure(bootstyle="info")

        def on_leave(e):
            self.configure(bootstyle="light")

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)

        # Make all child widgets trigger the same hover effect
        for child in self.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

    def _on_click(self):
        """Handle card click"""
        if self.on_click_callback:
            self.on_click_callback(self.supply_data['id'])
