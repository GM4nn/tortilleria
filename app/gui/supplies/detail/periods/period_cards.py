import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from datetime import datetime


MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


class PeriodCards(ttk.Frame):
    """Tabla de periodos de consumo"""

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
            {"text": "Notas", "stretch": True, "width": 120},
        ]

        rows = []
        for p in periods:
            purchase = p['purchase']
            consumption = p['consumption']
            prev_stock = purchase.get('initial_stock', 0.0)
            total = prev_stock + purchase['quantity']

            s, e = p['start_date'], p['end_date']
            desde = f"{s.day}/{MESES[s.month]}/{s.year}"
            hasta = f"{e.day}/{MESES[e.month]}/{e.year}"

            if consumption:
                consumed = consumption['quantity_consumed']
                remaining = consumption['quantity_remaining']
                pct = f"{consumed / total * 100:.0f}%" if total > 0 else "-"
                notes = (consumption.get('notes') or '')[:30]
            else:
                consumed = remaining = 0
                pct = "-"
                notes = ""

            rows.append([
                desde,
                hasta,
                f"{purchase['quantity']:.2f} {purchase['unit']}",
                f"{prev_stock:.2f}" if prev_stock > 0 else "-",
                f"{total:.2f}",
                f"{consumed:.2f}" if consumption else "-",
                f"{remaining:.2f}" if consumption else "-",
                pct,
                notes
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
        purchases = self.supply_data['purchases']
        if len(purchases) < 2:
            return []

        periods = []
        for i in range(len(purchases) - 1):
            curr = purchases[i]
            prev = purchases[i + 1]
            curr_date = self._to_date(curr['purchase_date'])
            prev_date = self._to_date(prev['purchase_date'])

            consumption = None
            for cons in self.supply_data['consumptions']:
                cs = self._to_date(cons['start_date'])
                ce = self._to_date(cons['end_date'])
                if cs >= prev_date and ce <= curr_date:
                    consumption = cons
                    break
                elif abs((cs - prev_date).days) <= 2 and abs((ce - curr_date).days) <= 2:
                    consumption = cons
                    break

            periods.append({
                'start_date': prev_date,
                'end_date': curr_date,
                'purchase': prev,
                'consumption': consumption,
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
