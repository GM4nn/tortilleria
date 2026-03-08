import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.cash.summary_panel import SummaryPanel
from app.gui.cash.register_form import RegisterForm
from app.gui.cash.closed_panel import ClosedPanel
from app.gui.cash.history_panel import HistoryPanel
from app.data.providers.cash_cut import cash_cut_provider


class CashContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.provider = cash_cut_provider
        self.setup_ui()

    def setup_ui(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Tab 1: Caja
        self.tab_caja = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_caja, text="  💰 Caja  ")
        self._build_caja_tab()

        # Tab 2: Historial de Caja
        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="  📋 Historial de Caja  ")
        self.setup_historial_tab()

    def _build_caja_tab(self):
        # Clear existing content
        for w in self.tab_caja.winfo_children():
            w.destroy()

        today_cut = self.provider.get_today_cut()

        if today_cut:
            # Cash is closed — show summary of the cut
            self.closed_panel = ClosedPanel(self.tab_caja, today_cut)
            self.closed_panel.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        else:
            # Cash is open — show indicators + form
            header = ttk.Frame(self.tab_caja)
            header.pack(fill=X, padx=20, pady=(20, 10))

            ttk.Label(
                header,
                text="Corte de Caja",
                font=("Segoe UI", 22, "bold"),
            ).pack(side=LEFT)

            self.summary_panel = SummaryPanel(self.tab_caja, self)
            self.summary_panel.pack(fill=X, padx=20, pady=(0, 10))

            self.register_form = RegisterForm(self.tab_caja, self)
            self.register_form.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 20))

    def setup_historial_tab(self):
        self.history_panel = HistoryPanel(self.tab_historial, self)
        self.history_panel.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def refresh_all(self):
        self._build_caja_tab()
        self.history_panel.refresh()
