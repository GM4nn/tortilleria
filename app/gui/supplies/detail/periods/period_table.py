import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.components.server_paginated_table import ServerPaginatedTableview
from app.data.providers.supplies import supply_provider
from datetime import datetime


MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

COLUMNS = [
    {"text": "Desde", "stretch": False, "width": 100},
    {"text": "Hasta", "stretch": False, "width": 100},
    {"text": "Compra", "stretch": False, "width": 100},
    {"text": "Sobrante", "stretch": False, "width": 80},
    {"text": "Disponible", "stretch": False, "width": 90},
    {"text": "Consumido", "stretch": False, "width": 90},
    {"text": "Restante", "stretch": False, "width": 90},
    {"text": "% Consumo", "stretch": True, "width": 90},
]


class PeriodTable(ttk.Frame):
    """Tabla de periodos de consumo con paginacion server-side"""

    def __init__(self, parent, supply_id):
        super().__init__(parent)
        self.supply_id = supply_id
        self.provider = supply_provider
        self.setup_ui()

    def setup_ui(self):
        count = self.provider.count_periods(self.supply_id)

        if count == 0:
            ttk.Label(
                self,
                text="No hay suficientes compras para crear periodos",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)
            return

        self.table = ServerPaginatedTableview(
            master=self,
            coldata=COLUMNS,
            fetch_page=self._fetch_page,
            count_rows=self._count_rows,
            pagesize=10,
            searchable=False,
            bootstyle=PRIMARY,
            height=10
        )
        self.table.pack(fill=BOTH, expand=YES)

    def _fetch_page(self, offset, limit):
        periods = self.provider.get_periods_paginated(self.supply_id, offset, limit)

        rows = []
        for p in periods:
            s = self._to_date(p['start_date'])
            e = self._to_date(p['end_date'])
            desde = f"{s.day}/{MESES[s.month]}/{s.year}" if s else "?"
            hasta = f"{e.day}/{MESES[e.month]}/{e.year}" if e else "?"

            total = p['total_available']
            consumed = p['consumed']
            remaining = p['remaining']
            prev_remaining = p['prev_remaining']
            pct = f"{consumed / total * 100:.0f}%" if total > 0 else "-"

            rows.append([
                desde,
                hasta,
                f"{p['quantity']:.2f} {p['unit']}",
                f"{prev_remaining:.2f}" if prev_remaining > 0 else "-",
                f"{total:.2f}",
                f"{consumed:.2f}",
                f"{remaining:.2f}",
                pct,
            ])

        return rows

    def _count_rows(self):
        return self.provider.count_periods(self.supply_id)

    @staticmethod
    def _to_date(value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        if hasattr(value, 'date') and callable(value.date):
            return value.date()
        if hasattr(value, 'year'):
            return value
        return None

    def refresh(self):
        if hasattr(self, 'table'):
            self.table.refresh()
