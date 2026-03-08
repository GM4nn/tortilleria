import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.cash_cut import cash_cut_provider


class SummaryPanel(ttk.Labelframe):
    def __init__(self, parent, content):
        super().__init__(parent, text="Resumen del Dia", padding=15)
        self.content = content
        self.provider = cash_cut_provider
        self.setup_ui()
        self.load_summary()

    def setup_ui(self):
        # Period info
        self.lbl_period = ttk.Label(
            self,
            text="Desde: ---",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        )
        self.lbl_period.pack(anchor=W, pady=(0, 10))

        # KPI Cards container
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=X)

        # Sales KPI
        self.sales_card = self._create_kpi_card(
            cards_frame, "Ventas Directas", "0", "$0.00", "info"
        )
        self.sales_card.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        # Orders KPI
        self.orders_card = self._create_kpi_card(
            cards_frame, "Pedidos Completados", "0", "$0.00", "warning"
        )
        self.orders_card.pack(side=LEFT, fill=X, expand=YES, padx=5)

        # Total KPI
        self.total_card = self._create_kpi_card(
            cards_frame, "Total Esperado", "", "$0.00", "success"
        )
        self.total_card.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

    def _create_kpi_card(self, parent, title, count_text, amount_text, style):
        card = ttk.Frame(parent, bootstyle=style, padding=10)

        ttk.Label(
            card,
            text=title,
            font=("Segoe UI", 9),
            bootstyle=f"inverse-{style}",
        ).pack(anchor=W)

        lbl_amount = ttk.Label(
            card,
            text=amount_text,
            font=("Segoe UI", 18, "bold"),
            bootstyle=f"inverse-{style}",
        )
        lbl_amount.pack(anchor=W, pady=(5, 0))

        lbl_count = ttk.Label(
            card,
            text=count_text,
            font=("Segoe UI", 9),
            bootstyle=f"inverse-{style}",
        )
        lbl_count.pack(anchor=W)

        card._lbl_amount = lbl_amount
        card._lbl_count = lbl_count
        return card

    def load_summary(self):
        summary = self.provider.get_current_period_summary()

        today_str = summary['today'].strftime("%d/%b/%Y")
        self.lbl_period.config(text=f"Fecha: {today_str}")

        self.sales_card._lbl_amount.config(text=f"${summary['sales_total']:,.2f}")
        self.sales_card._lbl_count.config(text=f"{summary['sales_count']} ventas")

        self.orders_card._lbl_amount.config(text=f"${summary['orders_total']:,.2f}")
        self.orders_card._lbl_count.config(text=f"{summary['orders_count']} pedidos")

        self.total_card._lbl_amount.config(text=f"${summary['expected_total']:,.2f}")
        self.total_card._lbl_count.config(text="")

        self.content.current_summary = summary
