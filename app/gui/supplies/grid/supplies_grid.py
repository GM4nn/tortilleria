import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from app.data.providers.supplies import supply_provider
from app.gui.supplies.grid.supply_card import SupplyCard


class SuppliesGrid(ttk.Frame):
    """Grid de tarjetas para mostrar insumos"""

    def __init__(self, parent, app, on_card_click, on_new_supply=None):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = supply_provider
        self.on_card_click = on_card_click
        self.on_new_supply = on_new_supply
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
        """Setup the scrollable grid section"""
        # Scrolled frame para las tarjetas
        self.scrolled_frame = ScrolledFrame(self, autohide=True)
        self.scrolled_frame.pack(fill=BOTH, expand=YES)

        # Frame interior para las tarjetas - usar el frame interno del ScrolledFrame
        # El ScrolledFrame de ttkbootstrap ya tiene un frame interno accesible
        self.cards_container = ttk.Frame(self.scrolled_frame)
        self.cards_container.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        # Bot\u00f3n de refrescar
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Refrescar",
            command=self.load_supplies,
            bootstyle="info-outline",
            width=15
        ).pack(side=LEFT)

        ttk.Button(
            btn_frame,
            text="Nuevo Insumo",
            command=self.new_supply,
            bootstyle="success",
            width=15
        ).pack(side=LEFT, padx=(10, 0))

    def load_supplies(self):
        """Load all supplies from database"""
        self.all_supplies = self.provider.get_all_supplies()
        self.display_supplies(self.all_supplies)

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

    def display_supplies(self, supplies):
        """Display supplies as cards in a grid"""
        # Limpiar tarjetas existentes
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        if not supplies:
            # Mostrar mensaje si no hay insumos
            no_data_label = ttk.Label(
                self.cards_container,
                text="No hay insumos registrados",
                font=("Arial", 12),
                bootstyle="secondary"
            )
            no_data_label.pack(pady=50)
            return

        # Crear grid de tarjetas (3 columnas)
        CARDS_PER_ROW = 3
        for idx, supply in enumerate(supplies):
            row = idx // CARDS_PER_ROW
            col = idx % CARDS_PER_ROW

            # Crear frame para la tarjeta con padding
            card_wrapper = ttk.Frame(self.cards_container)
            card_wrapper.grid(row=row, column=col, padx=5, pady=5, sticky=NSEW)

            # Crear la tarjeta
            card = SupplyCard(card_wrapper, supply, self.on_card_click)
            card.pack(fill=BOTH, expand=YES)

        # Configurar el grid para que las columnas se expandan uniformemente
        for col in range(CARDS_PER_ROW):
            self.cards_container.grid_columnconfigure(col, weight=1, uniform="cards")

    def new_supply(self):
        """Create a new supply"""
        if self.on_new_supply:
            self.on_new_supply()
