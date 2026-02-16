import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime


MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


class CurrentPeriodSummary(ttk.Frame):
    """Resumen colapsable del periodo de consumo actual"""

    def __init__(self, parent, supply_data):
        super().__init__(parent)
        self.supply_data = supply_data
        self.expanded = False
        self.content_frame = None

        self.setup_ui()

    def setup_ui(self):
        if not self.supply_data['consumptions']:
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
        consumptions = self.supply_data['consumptions']
        if not consumptions:
            return

        current = consumptions[0]

        start = self._to_date(current['start_date'])
        end = self._to_date(current['end_date'])

        start_str = f"{start.day}/{MESES[start.month]}/{start.year}" if start else str(current['start_date'])
        end_str = f"{end.day}/{MESES[end.month]}/{end.year}" if end else str(current['end_date'])

        card = ttk.Labelframe(parent, text=f" {start_str}  →  {end_str}", bootstyle="info", padding=10)
        card.pack(fill=X, pady=(0, 5))

        # Buscar compra del periodo
        period_purchase = None
        if start and self.supply_data['purchases']:
            for p in self.supply_data['purchases']:
                pd = self._to_date(p['purchase_date'])
                if pd and pd <= start:
                    period_purchase = p
                    break

        kpi_frame = ttk.Frame(card)
        kpi_frame.pack(fill=X)

        if period_purchase:
            self._kpi(kpi_frame, "Compra", f"{period_purchase['quantity']:.2f} {period_purchase['unit']}", "info")

        self._kpi(kpi_frame, "Consumido", f"{current['quantity_consumed']:.2f} {current['unit']}", "danger")
        self._kpi(kpi_frame, "Restante", f"{current['quantity_remaining']:.2f} {current['unit']}", "success")

        latest = self.supply_data['purchases'][0] if self.supply_data['purchases'] else None
        inv = current['quantity_remaining'] + (latest['quantity'] if latest else 0)
        self._kpi(kpi_frame, "Inventario Disponible", f"{inv:.2f} {current['unit']}", "primary")

        # Progress bar
        if period_purchase and period_purchase['quantity'] > 0:
            prev_stock = period_purchase.get('initial_stock', 0.0)
            total = prev_stock + period_purchase['quantity']
            if total > 0:
                pct = (current['quantity_consumed'] / total) * 100
                pf = ttk.Frame(card)
                pf.pack(fill=X, pady=(8, 0))
                ttk.Label(pf, text=f"Consumo: {pct:.1f}%", font=("Arial", 9), bootstyle="secondary").pack(side=LEFT, padx=(0, 10))
                ttk.Progressbar(pf, value=pct, bootstyle="danger" if pct > 75 else "warning" if pct > 50 else "success").pack(side=LEFT, fill=X, expand=YES)

        if current['notes']:
            ttk.Label(card, text=f"Nota: {current['notes']}", font=("Arial", 9, "italic"), bootstyle="secondary", wraplength=600).pack(anchor=W, pady=(5, 0))

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
