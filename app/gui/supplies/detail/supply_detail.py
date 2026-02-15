import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.supplies import supply_provider
from app.gui.supplies.detail.history.historial_tab import historyTab
from app.gui.supplies.detail.periods.periods_tab import periodsTab


class SupplyDetailView(ttk.Frame):
    """Vista de detalle de un insumo: header + tabs + contenido delegado"""

    def __init__(self, parent, app, supply_id, on_back_callback, on_edit_purchase_callback=None, on_tab_change_callback=None):
        super().__init__(parent)
        self.app = app
        self.supply_id = supply_id
        self.on_back_callback = on_back_callback
        self.on_edit_purchase_callback = on_edit_purchase_callback
        self.on_tab_change_callback = on_tab_change_callback
        self.provider = supply_provider
        self.supply_data = None

        self.load_supply_data()
        self.setup_ui()

    def load_supply_data(self):
        self.supply_data = self.provider.get_supply_by_id(self.supply_id)

    def setup_ui(self):
        if not self.supply_data:
            ttk.Label(self, text="Insumo no encontrado", font=("Arial", 14, "bold")).pack(pady=50)
            return

        main_layout = ttk.Frame(self)
        main_layout.pack(fill=BOTH, expand=YES)

        self.setup_header(main_layout)
        self.setup_tabs(main_layout)

        # Frame contenedor para el tab activo
        self.tab_content_frame = ttk.Frame(main_layout)
        self.tab_content_frame.pack(fill=BOTH, expand=YES)

        self._show_history_tab()

    def setup_header(self, parent):
        header = ttk.Frame(parent)
        header.pack(fill=X, pady=(0, 8))

        ttk.Button(
            header, text="← Volver", command=self.on_back_callback,
            bootstyle="secondary-outline", width=10
        ).pack(side=LEFT, padx=(0, 15))

        ttk.Label(header, text=self.supply_data['supply_name'], font=("Arial", 16, "bold")).pack(side=LEFT)
        ttk.Label(header, text="·", font=("Arial", 16), bootstyle="secondary").pack(side=LEFT, padx=10)
        ttk.Label(header, text=self.supply_data['supplier_name'], font=("Arial", 12), bootstyle="secondary").pack(side=LEFT)

    def setup_tabs(self, parent):
        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=(0, 8))

        tab_frame = ttk.Frame(parent)
        tab_frame.pack(fill=X, pady=(0, 8))

        self.current_tab = "history"

        self.history_btn = ttk.Button(
            tab_frame, text="history de Compras",
            command=lambda: self._switch_tab("history"),
            bootstyle="primary", width=20
        )
        self.history_btn.pack(side=LEFT, padx=(0, 5))

        self.periods_btn = ttk.Button(
            tab_frame, text="Períodos",
            command=lambda: self._switch_tab("periods"),
            bootstyle="secondary-outline", width=20
        )
        self.periods_btn.pack(side=LEFT)

    # ─── Tab switching ────────────────────────────────────────────

    def _switch_tab(self, tab_name):
        if tab_name == self.current_tab:
            return

        self.current_tab = tab_name

        if self.on_tab_change_callback:
            self.on_tab_change_callback(tab_name)

        if tab_name == "history":
            self.history_btn.configure(bootstyle="primary")
            self.periods_btn.configure(bootstyle="secondary-outline")
            self._show_history_tab()
        else:
            self.history_btn.configure(bootstyle="secondary-outline")
            self.periods_btn.configure(bootstyle="primary")
            self._show_periods_tab()

    def _show_history_tab(self):
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        self.history_tab = historyTab(
            self.tab_content_frame,
            self.supply_data,
            on_edit_purchase_callback=self.on_edit_purchase_callback
        )
        self.history_tab.pack(fill=BOTH, expand=YES)

    def _show_periods_tab(self):
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        self.periods_tab = periodsTab(
            self.tab_content_frame,
            self.supply_data
        )
        self.periods_tab.pack(fill=BOTH, expand=YES)

    def refresh(self):
        self.load_supply_data()
        if self.supply_data and self.current_tab == "history":
            if hasattr(self, 'history_tab') and self.history_tab.winfo_exists():
                self.history_tab.refresh(self.supply_data)
