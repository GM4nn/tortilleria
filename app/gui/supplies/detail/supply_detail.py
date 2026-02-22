import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.supplies import supply_provider
from app.gui.supplies.detail.history.content import HistoryContent
from app.gui.supplies.detail.periods.content import PeriodsContent


class SupplyDetailView(ttk.Frame):
    """Vista de detalle de un insumo: header + tabs + contenido"""

    def __init__(self, parent, app, supply_id, on_back_callback):
        super().__init__(parent)
        self.app = app
        self.supply_id = supply_id
        self.on_back_callback = on_back_callback
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

        # Left: header + tabs + tab content
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))

        self.setup_header(self.left_frame)
        self.setup_tabs(self.left_frame)

        self.tab_content_frame = ttk.Frame(self.left_frame)
        self.tab_content_frame.pack(fill=BOTH, expand=YES)

        # Right: sidebar para purchase form (manejado por HistoryContent)
        self.right_frame = ttk.Frame(self, width=400)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(5, 0))

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
        if self.supply_data.get('unit'):
            ttk.Label(header, text="·", font=("Arial", 16), bootstyle="secondary").pack(side=LEFT, padx=10)
            ttk.Label(header, text=self.supply_data['unit'], font=("Arial", 12), bootstyle="info").pack(side=LEFT)

    def setup_tabs(self, parent):
        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=(0, 8))

        tab_frame = ttk.Frame(parent)
        tab_frame.pack(fill=X, pady=(0, 8))

        self.current_tab = "history"

        self.history_btn = ttk.Button(
            tab_frame, text="Historial de Compras",
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

        if tab_name == "history":
            self.history_btn.configure(bootstyle="primary")
            self.periods_btn.configure(bootstyle="secondary-outline")
            self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(5, 0))
            self._show_history_tab()
        else:
            self.history_btn.configure(bootstyle="secondary-outline")
            self.periods_btn.configure(bootstyle="primary")
            self.right_frame.pack_forget()
            self._show_periods_tab()

    def _clear_tab(self):
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def _show_history_tab(self):
        self._clear_tab()

        self.history_content = HistoryContent(
            self.tab_content_frame,
            self.right_frame,
            self.app,
            self.supply_data,
            on_form_saved=self._on_form_saved
        )

    def _show_periods_tab(self):
        self._clear_tab()

        self.periods_tab = PeriodsContent(
            self.tab_content_frame,
            self.supply_data
        )
        self.periods_tab.pack(fill=BOTH, expand=YES)

    # ─── Callbacks ────────────────────────────────────────────────

    def _on_form_saved(self):
        self.load_supply_data()
        if self.supply_data and self.current_tab == "history":
            self.history_content.refresh(self.supply_data)
            self.history_content.reset_form()

    def refresh(self):
        self.load_supply_data()
        if self.supply_data and self.current_tab == "history" and hasattr(self, 'history_content'):
            self.history_content.refresh(self.supply_data)
