import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.cash.summary_panel import SummaryPanel
from app.gui.cash.register_form import RegisterForm
from app.gui.cash.history_panel import HistoryPanel
from app.data.providers.cash_cut import cash_cut_provider


class CashContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.provider = cash_cut_provider
        self.setup_ui()

    def setup_ui(self):
        # Title
        header = ttk.Frame(self)
        header.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="Corte de Caja",
            font=("Segoe UI", 22, "bold"),
        ).pack(side=LEFT)

        # Top section: Summary (left) + Register form (right)
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=X, padx=20, pady=(0, 10))

        self.summary_panel = SummaryPanel(top_frame, self)
        self.summary_panel.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.register_form = RegisterForm(top_frame, self)
        self.register_form.pack(side=LEFT, fill=BOTH, expand=YES)

        # Bottom section: History
        self.history_panel = HistoryPanel(self, self)
        self.history_panel.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 20))

    def refresh_all(self):
        self.summary_panel.load_summary()
        self.register_form.reset_form()
        self.history_panel.refresh()
