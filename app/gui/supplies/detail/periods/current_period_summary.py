import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime


MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


class CurrentPeriodSummary(ttk.Frame):
    """Resumen colapsable del periodo de consumo actual (derivado de las 2 compras mas recientes)"""

    def __init__(self, parent, supply_data):
        super().__init__(parent)
        self.supply_data = supply_data
        self.expanded = False
        self.content_frame = None

        self.setup_ui()

    def setup_ui(self):
        purchases = self.supply_data.get('purchases', [])
        if len(purchases) < 2:
            return

        header = ttk.Frame(self)
        header.pack(fill=X)

        self.collapse_icon = ttk.Label(header, text="▶", font=("Arial", 10), bootstyle="info", cursor="hand2")
        self.collapse_icon.pack(side=LEFT, padx=(0, 6))

        title = ttk.Label(header, text="Resumen del Periodo Actual", font=("Arial", 11, "bold"), bootstyle="info", cursor="hand2")
        title.pack(side=LEFT)

        for w in [header, self.collapse_icon, title]:
            w.bind('<Button-1>', lambda e: self._toggle())

        self.content_frame = ttk.Frame(self)
        self._build_summary(self.content_frame)

    def _toggle(self):
        if self.expanded:
            self.content_frame.pack_forget()
            self.collapse_icon.configure(text="▶")
            self.expanded = False
        else:
            self.content_frame.pack(fill=X, pady=(5, 0))
            self.collapse_icon.configure(text="▼")
            self.expanded = True

    def _build_summary(self, parent):
        purchases = self.supply_data.get('purchases', [])
        if len(purchases) < 2:
            return

        latest = purchases[0]    # compra mas reciente
        previous = purchases[1]  # compra anterior

        # Derivar consumo entre las 2 compras
        prev_remaining = previous.get('remaining', 0.0)
        total_available = prev_remaining + previous['quantity']
        curr_remaining = latest.get('remaining', 0.0)
        consumed = max(0, total_available - curr_remaining)

        start = self._to_date(previous['purchase_date'])
        end = self._to_date(latest['purchase_date'])
        unit = previous.get('unit', '')

        start_str = f"{start.day}/{MESES[start.month]}/{start.year}" if start else "?"
        end_str = f"{end.day}/{MESES[end.month]}/{end.year}" if end else "?"

        card = ttk.Labelframe(parent, text=f" {start_str}  →  {end_str}", bootstyle="info", padding=10)
        card.pack(fill=X, pady=(0, 5))

        kpi_frame = ttk.Frame(card)
        kpi_frame.pack(fill=X)

        self._kpi(kpi_frame, "Compra", f"{previous['quantity']:.2f} {unit}", "info")
        self._kpi(kpi_frame, "Consumido", f"{consumed:.2f} {unit}", "danger")
        self._kpi(kpi_frame, "Restante", f"{curr_remaining:.2f} {unit}", "success")

        # Inventario disponible = remaining + quantity de la ultima compra
        inv = curr_remaining + latest['quantity']
        self._kpi(kpi_frame, "Inventario Disponible", f"{inv:.2f} {unit}", "primary")

        # Progress bar
        if total_available > 0:
            pct = (consumed / total_available) * 100
            pf = ttk.Frame(card)
            pf.pack(fill=X, pady=(8, 0))
            ttk.Label(pf, text=f"Consumo: {pct:.1f}%", font=("Arial", 9), bootstyle="secondary").pack(side=LEFT, padx=(0, 10))
            ttk.Progressbar(pf, value=pct, bootstyle="danger" if pct > 75 else "warning" if pct > 50 else "success").pack(side=LEFT, fill=X, expand=YES)

    def _kpi(self, parent, label, value, style):
        f = ttk.Frame(parent)
        f.pack(side=LEFT, fill=X, expand=YES, padx=(0, 15))
        ttk.Label(f, text=label, font=("Arial", 9), bootstyle="secondary").pack(anchor=W)
        ttk.Label(f, text=value, font=("Arial", 12, "bold"), bootstyle=style).pack(anchor=W)

    @staticmethod
    def _to_date(value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        if hasattr(value, 'date') and callable(value.date):
            return value.date()
        if hasattr(value, 'year'):
            return value
        return None
