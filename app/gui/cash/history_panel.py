import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
from app.constants import mexico_now
from app.data.providers.cash_cut import cash_cut_provider
from app.gui.components.server_paginated_table import ServerPaginatedTableview


class HistoryPanel(ttk.Frame):
    def __init__(self, parent, content):
        super().__init__(parent, padding=10)
        self.content = content
        self.provider = cash_cut_provider
        self._filters = None
        self.setup_ui()

    def setup_ui(self):
        self.setup_header()
        self.setup_date_filter()
        self.setup_table()

    def setup_header(self):
        header = ttk.Frame(self)
        header.pack(fill=X, pady=(10, 10), padx=10)

        ttk.Label(
            header,
            text="Historial de Cortes",
            font=("Segoe UI", 18, "bold"),
        ).pack(side=LEFT)

        ttk.Button(
            header,
            text="Actualizar",
            command=self.refresh,
            bootstyle="info-outline",
        ).pack(side=RIGHT)

    def setup_date_filter(self):
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=X, padx=10, pady=(0, 10))

        today = mexico_now()
        start_of_month = today.replace(day=1)

        ttk.Label(filter_frame, text="Fecha:").pack(side=LEFT)

        self.date_start = DateEntry(
            filter_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y",
            startdate=start_of_month,
        )
        self.date_start.pack(side=LEFT, padx=(5, 0))

        ttk.Label(filter_frame, text="hasta").pack(side=LEFT, padx=5)

        self.date_end = DateEntry(
            filter_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y",
        )
        self.date_end.pack(side=LEFT)

        ttk.Button(
            filter_frame,
            text="Filtrar",
            command=self._apply_filter,
            bootstyle="info-outline",
        ).pack(side=LEFT, padx=(10, 5))

        ttk.Button(
            filter_frame,
            text="Limpiar",
            command=self._clear_filter,
            bootstyle="secondary-outline",
        ).pack(side=LEFT)

    def setup_table(self):
        columns = [
            {"text": "#", "stretch": False, "width": 50},
            {"text": "Fecha Cierre", "stretch": True, "width": 140},
            {"text": "Ventas", "stretch": False, "width": 60},
            {"text": "Pedidos", "stretch": False, "width": 60},
            {"text": "Efectivo", "stretch": True, "width": 100},
            {"text": "Tarjeta", "stretch": True, "width": 100},
            {"text": "Transferencia", "stretch": True, "width": 100},
            {"text": "Declarado", "stretch": True, "width": 100},
            {"text": "Esperado", "stretch": True, "width": 100},
            {"text": "Diferencia", "stretch": True, "width": 100},
        ]

        self.table = ServerPaginatedTableview(
            master=self,
            coldata=columns,
            fetch_page=self._fetch_page,
            count_rows=lambda: self.provider.get_count(self._filters),
            pagesize=40,
            bootstyle=PRIMARY,
        )
        self.table.pack(fill=BOTH, expand=YES, padx=10)

    def _fetch_page(self, offset, limit):
        rows = self.provider.get_all(offset=offset, limit=limit, filters=self._filters)
        table_data = []
        for row in rows:
            cut_id, closed_at, expected, cash, card, transfer, declared, diff, s_count, o_count = row
            date_str = closed_at.strftime("%d/%b/%Y %H:%M") if closed_at else "---"

            if abs(diff) < 0.01:
                diff_str = "$0.00"
            elif diff > 0:
                diff_str = f"+${diff:,.2f}"
            else:
                diff_str = f"-${abs(diff):,.2f}"

            table_data.append([
                cut_id,
                date_str,
                s_count,
                o_count,
                f"${cash:,.2f}",
                f"${card:,.2f}",
                f"${transfer:,.2f}",
                f"${declared:,.2f}",
                f"${expected:,.2f}",
                diff_str,
            ])
        return table_data

    def _apply_filter(self):
        start = self.date_start.entry.get()
        end = self.date_end.entry.get()
        try:
            start_date = datetime.strptime(start, "%d/%m/%Y").date()
            end_date = datetime.strptime(end, "%d/%m/%Y").date()
            self._filters = self.provider.build_date_range_filter(start_date, end_date)
        except ValueError:
            self._filters = None
        self.table.refresh()

    def _clear_filter(self):
        self.date_start.entry.delete(0, "end")
        self.date_end.entry.delete(0, "end")
        self._filters = None
        self.table.refresh()

    def refresh(self):
        self.table.refresh()
