import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.supplies import supply_provider
from app.gui.supplies.detail.history.historial_tab import historyTab
from app.gui.supplies.detail.history.purchase_form import PurchaseForm
from app.gui.supplies.detail.periods.periodos_tab import periodsTab


class SupplyDetailView(ttk.Frame):
    """Vista de detalle de un insumo: header + tabs + contenido + sidebar de compras"""

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

        # Right: purchase form sidebar
        self.right_frame = ttk.Frame(self, width=400)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side=RIGHT, fill=BOTH, padx=(5, 0))

        self.purchase_form = PurchaseForm(
            self.right_frame,
            self.app,
            on_close_callback=self._on_form_saved
        )
        self.purchase_form.pack(fill=BOTH, expand=YES)
        self.purchase_form.set_supply(
            self.supply_id,
            self.supply_data['supply_name'],
            self.supply_data.get('supplier_id')
        )

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
            self._reset_form_to_new()
            self._show_history_tab()
        else:
            self.history_btn.configure(bootstyle="secondary-outline")
            self.periods_btn.configure(bootstyle="primary")
            self.right_frame.pack_forget()
            self._show_periods_tab()

    def _show_history_tab(self):
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        self.history_tab = historyTab(
            self.tab_content_frame,
            self.supply_data,
            on_edit_purchase_callback=self._on_purchase_selected
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

    # ─── Purchase form management ─────────────────────────────────

    def _on_purchase_selected(self, supply_id, supply_name, purchase_data):
        """Al hacer click en una fila de compra, cargar en el form"""
        self.purchase_form.clear_form()
        self.purchase_form.set_edit_mode(supply_id, supply_name, purchase_data)

    def _on_form_saved(self):
        """Al guardar/cancelar, refrescar data y resetear form"""
        self.load_supply_data()
        if self.supply_data and self.current_tab == "history":
            if hasattr(self, 'history_tab') and self.history_tab.winfo_exists():
                self.history_tab.refresh(self.supply_data)
        self._reset_form_to_new()

    def _reset_form_to_new(self):
        """Resetear form a modo nueva compra"""
        if not self.supply_data:
            return
        self.purchase_form.clear_form()
        self.purchase_form.set_supply(
            self.supply_id,
            self.supply_data['supply_name'],
            self.supply_data.get('supplier_id')
        )

    def refresh(self):
        self.load_supply_data()
        if self.supply_data and self.current_tab == "history":
            if hasattr(self, 'history_tab') and self.history_tab.winfo_exists():
                self.history_tab.refresh(self.supply_data)
