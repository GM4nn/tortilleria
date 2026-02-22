import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from datetime import datetime


MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


class PeriodCards(ttk.Frame):
    """Tabla de periodos de consumo derivados de compras consecutivas"""

    def __init__(self, parent, supply_data):
        super().__init__(parent)
        self.supply_data = supply_data
        self.setup_ui()

    def setup_ui(self):
        if not self.supply_data['purchases']:
            ttk.Label(self, text="No hay compras registradas", font=("Arial", 10), bootstyle="secondary").pack(pady=20)
            return

        periods = self._create_periods()

        if not periods:
            ttk.Label(self, text="No hay suficientes compras para crear periodos", font=("Arial", 10), bootstyle="secondary").pack(pady=20)
            return

        columns = [
            {"text": "Desde", "stretch": False, "width": 100},
            {"text": "Hasta", "stretch": False, "width": 100},
            {"text": "Compra", "stretch": False, "width": 100},
            {"text": "Sobrante", "stretch": False, "width": 80},
            {"text": "Disponible", "stretch": False, "width": 90},
            {"text": "Consumido", "stretch": False, "width": 90},
            {"text": "Restante", "stretch": False, "width": 90},
            {"text": "% Consumo", "stretch": False, "width": 90},
        ]

        rows = []
        for p in periods:
            prev = p['purchase']
            prev_remaining = prev.get('remaining', 0.0)
            total = prev_remaining + prev['quantity']

            s, e = p['start_date'], p['end_date']
            desde = f"{s.day}/{MESES[s.month]}/{s.year}"
            hasta = f"{e.day}/{MESES[e.month]}/{e.year}"

            consumed = p['consumed']
            remaining = p['remaining']
            pct = f"{consumed / total * 100:.0f}%" if total > 0 else "-"

            rows.append([
                desde,
                hasta,
                f"{prev['quantity']:.2f} {prev['unit']}",
                f"{prev_remaining:.2f}" if prev_remaining > 0 else "-",
                f"{total:.2f}",
                f"{consumed:.2f}",
                f"{remaining:.2f}",
                pct,
            ])

        self.table = Tableview(
            master=self,
            coldata=columns,
            rowdata=rows,
            paginated=True,
            searchable=False,
            bootstyle=PRIMARY,
            pagesize=10,
            height=10
        )
        self.table.pack(fill=BOTH, expand=YES)

    # ─── Crear periodos ───────────────────────────────────────────

    def _create_periods(self):
        """Derivar periodos de consumo a partir de compras consecutivas.
        consumed = (prev.remaining + prev.quantity) - curr.remaining
        """
        purchases = self.supply_data['purchases']
        if len(purchases) < 2:
            return []

        periods = []
        for i in range(len(purchases) - 1):
            curr = purchases[i]      # compra mas reciente
            prev = purchases[i + 1]  # compra anterior
            curr_date = self._to_date(curr['purchase_date'])
            prev_date = self._to_date(prev['purchase_date'])

            prev_remaining = prev.get('remaining', 0.0)
            total_available = prev_remaining + prev['quantity']
            curr_remaining = curr.get('remaining', 0.0)
            consumed = max(0, total_available - curr_remaining)

            periods.append({
                'start_date': prev_date,
                'end_date': curr_date,
                'purchase': prev,
                'consumed': consumed,
                'remaining': curr_remaining,
                'total_available': total_available,
            })

        return periods

    @staticmethod
    def _to_date(value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        if hasattr(value, 'date') and callable(value.date):
            return value.date()
        if hasattr(value, 'year'):
            return value
        return None
