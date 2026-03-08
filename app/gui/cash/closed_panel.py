import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ClosedPanel(ttk.Frame):
    """Panel that shows when today's cash cut is already registered."""

    def __init__(self, parent, cut_data):
        super().__init__(parent)
        self.cut = cut_data
        self.setup_ui()

    def setup_ui(self):
        cut = self.cut

        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text="Caja Cerrada",
            font=("Segoe UI", 22, "bold"),
        ).pack(side=LEFT)

        date_str = cut['closed_at'].strftime("%d/%b/%Y %H:%M")
        ttk.Label(
            header,
            text=f"Corte #{cut['id']}  —  {date_str}",
            font=("Segoe UI", 11),
            bootstyle="secondary",
        ).pack(side=RIGHT)

        # KPI Cards: Ventas y Pedidos
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=X, padx=20, pady=(0, 15))

        sales_card = self._create_kpi_card(
            cards_frame, "Ventas Directas",
            f"${cut['sales_total']:,.2f}", f"{cut['sales_count']} ventas", "info",
        )
        sales_card.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        orders_card = self._create_kpi_card(
            cards_frame, "Pedidos Completados",
            f"${cut['orders_total']:,.2f}", f"{cut['orders_count']} pedidos", "warning",
        )
        orders_card.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

        # Desglose de pagos (cards en fila, sin frame contenedor)
        ttk.Label(
            self, text="Desglose de Pagos",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor=W, padx=20, pady=(5, 8))

        payments_frame = ttk.Frame(self)
        payments_frame.pack(fill=X, padx=20, pady=(0, 15))

        payments = [
            ("Efectivo", f"${cut['declared_cash']:,.2f}"),
            ("Tarjeta", f"${cut['declared_card']:,.2f}"),
            ("Transferencia", f"${cut['declared_transfer']:,.2f}"),
        ]

        for i, (label, value) in enumerate(payments):
            px = (0, 5) if i == 0 else (5, 0) if i == len(payments) - 1 else 5
            card = ttk.Frame(payments_frame, bootstyle="dark", padding=10)
            card.pack(side=LEFT, fill=X, expand=YES, padx=px)

            ttk.Label(
                card, text=label,
                font=("Segoe UI", 9), bootstyle="inverse-dark",
            ).pack(anchor=W)
            ttk.Label(
                card, text=value,
                font=("Segoe UI", 16, "bold"), bootstyle="inverse-dark",
            ).pack(anchor=W, pady=(3, 0))

        # Total declarado bar
        declared_bar = ttk.Frame(self, bootstyle="primary", padding=0)
        declared_bar.pack(fill=X, padx=20, pady=(0, 5))

        ttk.Label(
            declared_bar, text="TOTAL DECLARADO:",
            font=("Segoe UI", 11, "bold"), bootstyle="inverse-primary",
        ).pack(side=LEFT, padx=10, pady=8)

        ttk.Label(
            declared_bar, text=f"${cut['declared_total']:,.2f}",
            font=("Segoe UI", 14, "bold"), bootstyle="inverse-primary",
        ).pack(side=RIGHT, padx=10, pady=8)

        # Total esperado bar
        expected_bar = ttk.Frame(self, bootstyle="secondary", padding=0)
        expected_bar.pack(fill=X, padx=20, pady=(0, 5))

        ttk.Label(
            expected_bar, text="TOTAL ESPERADO:",
            font=("Segoe UI", 11, "bold"), bootstyle="inverse-secondary",
        ).pack(side=LEFT, padx=10, pady=8)

        ttk.Label(
            expected_bar, text=f"${cut['expected_total']:,.2f}",
            font=("Segoe UI", 14, "bold"), bootstyle="inverse-secondary",
        ).pack(side=RIGHT, padx=10, pady=8)

        # Diferencia bar
        diff = cut['difference']
        if abs(diff) < 0.01:
            diff_text, diff_style = "$0.00  —  Exacto", "success"
        elif diff > 0:
            diff_text, diff_style = f"+${diff:,.2f}  —  Sobrante", "info"
        else:
            diff_text, diff_style = f"-${abs(diff):,.2f}  —  Faltante", "danger"

        diff_bar = ttk.Frame(self, bootstyle=diff_style, padding=0)
        diff_bar.pack(fill=X, padx=20, pady=(0, 15))

        ttk.Label(
            diff_bar, text="DIFERENCIA:",
            font=("Segoe UI", 11, "bold"), bootstyle=f"inverse-{diff_style}",
        ).pack(side=LEFT, padx=10, pady=8)

        ttk.Label(
            diff_bar, text=diff_text,
            font=("Segoe UI", 14, "bold"), bootstyle=f"inverse-{diff_style}",
        ).pack(side=RIGHT, padx=10, pady=8)

        # Notes
        if cut.get('notes'):
            notes_frame = ttk.Frame(self)
            notes_frame.pack(fill=X, padx=20, pady=(0, 15))
            ttk.Label(
                notes_frame, text="Notas:",
                font=("Segoe UI", 10, "bold"), bootstyle="secondary",
            ).pack(side=LEFT)
            ttk.Label(
                notes_frame, text=cut['notes'],
                font=("Segoe UI", 10),
            ).pack(side=LEFT, padx=(8, 0))

    def _create_kpi_card(self, parent, title, amount, count, style):
        card = ttk.Frame(parent, bootstyle=style, padding=10)

        ttk.Label(
            card, text=title,
            font=("Segoe UI", 9), bootstyle=f"inverse-{style}",
        ).pack(anchor=W)

        ttk.Label(
            card, text=amount,
            font=("Segoe UI", 18, "bold"), bootstyle=f"inverse-{style}",
        ).pack(anchor=W, pady=(5, 0))

        if count:
            ttk.Label(
                card, text=count,
                font=("Segoe UI", 9), bootstyle=f"inverse-{style}",
            ).pack(anchor=W)

        return card
