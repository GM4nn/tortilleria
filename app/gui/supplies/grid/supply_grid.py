import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from app.data.providers.supplies import supply_provider


class SupplyGrid(ttk.Frame):
    """Grid de tarjetas para mostrar insumos"""

    CARDS_PER_ROW = 3

    def __init__(self, parent, app, on_card_click, on_edit_supply=None):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = supply_provider
        self.on_card_click = on_card_click
        self.on_edit_supply = on_edit_supply
        self.all_supplies = []

        self.setup_ui()
        self.load_supplies()

    def setup_ui(self):
        """Setup the grid UI"""

        # Use self as the container instead of creating a left_frame
        self.setup_header()
        self.setup_grid_section()

    def setup_header(self):
        """Setup header with title and search"""
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(0, 10))

        ttk.Label(
            header,
            text="Gesti\u00f3n de Insumos",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT)

        search_frame = ttk.Frame(header)
        search_frame.pack(side=RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_supplies())

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=RIGHT)

    def setup_grid_section(self):
        
        # Scrolled frame para las tarjetas
        self.scrolled_frame = ScrolledFrame(self, autohide=True)
        self.scrolled_frame.pack(fill=BOTH, expand=YES)

        # Frame interior para las tarjetas - usar el frame interno del ScrolledFrame
        # El ScrolledFrame de ttkbootstrap ya tiene un frame interno accesible
        self.cards_container = ttk.Frame(self.scrolled_frame)
        self.cards_container.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Refrescar",
            command=self.load_supplies,
            bootstyle="info-outline",
            width=15
        ).pack(side=LEFT)

    def load_supplies(self):
        """Load all supplies from database"""
        self.all_supplies = self.provider.get_all_supplies()
        self.display_supplies(self.all_supplies)

    def display_supplies(self, supplies):
        """Display supplies as cards in a grid"""

        for widget in self.cards_container.winfo_children():
            widget.destroy()

        if not supplies:

            no_data_label = ttk.Label(
                self.cards_container,
                text="No hay insumos registrados",
                font=("Arial", 12),
                bootstyle="secondary"
            )
            no_data_label.pack(pady=50)
            return

        # Crear grid de tarjetas (3 columnas)
        for idx, supply in enumerate(supplies):
            row = idx // self.CARDS_PER_ROW
            col = idx % self.CARDS_PER_ROW

            # Crear la tarjeta directamente
            card = self.create_card(self.cards_container, supply)
            card.grid(row=row, column=col, padx=5, pady=5, sticky=NSEW)

        # Configurar el grid para que las columnas se expandan uniformemente
        for col in range(self.CARDS_PER_ROW):
            self.cards_container.grid_columnconfigure(col, weight=1, uniform="cards")

    def create_card(self, parent, supply_data):

        card = ttk.Frame(parent, bootstyle="light", relief=RAISED, borderwidth=1)

        container = ttk.Frame(card, padding=15)
        container.pack(fill=BOTH, expand=YES)

        # Nombre del insumo + botón editar
        name_frame = ttk.Frame(container)
        name_frame.pack(fill=X, pady=(0, 5))

        ttk.Label(
            name_frame,
            text=supply_data['supply_name'],
            font=("Arial", 14, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        ttk.Button(
            name_frame,
            text="\u270F",
            command=lambda s=supply_data: self._edit_supply(s),
            bootstyle="warning-outline",
            width=3
        ).pack(side=RIGHT)

        # Proveedor
        supplier_frame = ttk.Frame(container)
        supplier_frame.pack(fill=X, pady=2)

        ttk.Label(supplier_frame, text="Proveedor: ", font=("Arial", 9)).pack(side=LEFT)
        ttk.Label(
            supplier_frame,
            text=supply_data['supplier_name'],
            font=("Arial", 9, "bold"),
            bootstyle="info"
        ).pack(side=LEFT)

        ttk.Separator(container, orient=HORIZONTAL).pack(fill=X, pady=10)

        ttk.Button(
            container,
            text="Ver Detalles",
            command=lambda sid=supply_data['id']: self.on_card_click(sid),
            bootstyle="primary-outline",
            width=15
        ).pack(anchor=E)

        # Hover effect
        def on_enter(e):
            card.configure(bootstyle="info")

        def on_leave(e):
            card.configure(bootstyle="light")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        for child in card.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

        return card

    def _edit_supply(self, supply_data):
        """Enviar datos del insumo al formulario para editar"""

        if self.on_edit_supply:
            self.on_edit_supply(supply_data)

    def filter_supplies(self):
        """Filter supplies based on search term"""
        search_term = self.search_var.get().lower()

        if not search_term:
            self.display_supplies(self.all_supplies)
            return

        filtered = [
            s for s in self.all_supplies
            if search_term in s['supply_name'].lower() or
               search_term in s['supplier_name'].lower()
        ]

        self.display_supplies(filtered)