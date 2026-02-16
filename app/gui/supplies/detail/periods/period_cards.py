import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime


MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}


class PeriodCards(ttk.Frame):
    """Grid paginado de cards de periodos de consumo"""

    PERIODS_PER_PAGE = 4  # 2 columnas x 2 filas

    def __init__(self, parent, supply_data):
        super().__init__(parent)
        self.supply_data = supply_data
        self.all_periods = []
        self.current_page = 0
        self.total_pages = 0

        self.setup_ui()

    def setup_ui(self):
        if not self.supply_data['purchases']:
            ttk.Label(self, text="No hay compras registradas para este insumo", font=("Arial", 10), bootstyle="secondary").pack(pady=20)
            return

        self.all_periods = self._create_periods()

        if not self.all_periods:
            ttk.Label(self, text="No hay suficientes compras para crear periodos", font=("Arial", 10), bootstyle="secondary").pack(pady=20)
            return

        self.total_pages = (len(self.all_periods) + self.PERIODS_PER_PAGE - 1) // self.PERIODS_PER_PAGE

        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES)

        self.scrolled = ScrolledFrame(main_container, autohide=True)
        self.scrolled.pack(fill=BOTH, expand=YES)
        self.cards_frame = self.scrolled

        # Paginacion
        pagination_frame = ttk.Frame(main_container)
        pagination_frame.pack(fill=X, pady=(10, 5))

        self.prev_btn = ttk.Button(pagination_frame, text="« Anterior", command=self._prev_page, bootstyle="secondary-outline", width=12)
        self.prev_btn.pack(side=LEFT, padx=5)

        self.page_label = ttk.Label(pagination_frame, text="", font=("Arial", 10))
        self.page_label.pack(side=LEFT, expand=YES)

        self.next_btn = ttk.Button(pagination_frame, text="Siguiente »", command=self._next_page, bootstyle="secondary-outline", width=12)
        self.next_btn.pack(side=RIGHT, padx=5)

        self._render_page()

    # ─── Paginacion ───────────────────────────────────────────────

    def _render_page(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        for col in range(2):
            self.cards_frame.columnconfigure(col, weight=1, uniform="col")

        start_idx = self.current_page * self.PERIODS_PER_PAGE
        end_idx = min(start_idx + self.PERIODS_PER_PAGE, len(self.all_periods))

        for i, period in enumerate(self.all_periods[start_idx:end_idx]):
            self._create_card(self.cards_frame, period, i // 2, i % 2)

        self.page_label.configure(text=f"Pagina {self.current_page + 1} de {self.total_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages - 1 else "disabled")

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._render_page()

    # ─── Card ─────────────────────────────────────────────────────

    def _create_card(self, parent, period, row, col):
        s = period['start_date']
        e = period['end_date']
        start_str = f"{s.day}/{MESES[s.month]}/{s.year}"
        end_str = f"{e.day}/{MESES[e.month]}/{e.year}"

        style = "success" if period['is_current'] else "info"
        card = ttk.Labelframe(parent, text=f" {start_str} - {end_str}" + (" (Actual)" if period['is_current'] else ""), bootstyle=style, padding=8)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        purchase = period['purchase']
        consumption = period['consumption']
        prev_stock = purchase.get('initial_stock', 0.0)

        if prev_stock > 0:
            ttk.Label(card, text="Sobro del periodo anterior", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
            ttk.Label(card, text=f"{prev_stock:.2f} {purchase['unit']}", font=("Arial", 16, "bold"), bootstyle="secondary").pack(anchor=W, pady=(0, 3))

        ttk.Label(card, text="Compra", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
        ttk.Label(card, text=f"{purchase['quantity']:.2f} {purchase['unit']}", font=("Arial", 18, "bold"), bootstyle="info").pack(anchor=W)

        total = prev_stock + purchase['quantity']
        if prev_stock > 0:
            ttk.Label(card, text=f"Total: {total:.2f} {purchase['unit']}", font=("Arial", 11, "italic"), bootstyle="info").pack(anchor=W, pady=(0, 3))

        ttk.Separator(card, orient=HORIZONTAL).pack(fill=X, pady=3)

        if consumption:
            ttk.Label(card, text="Consumido", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
            ttk.Label(card, text=f"{consumption['quantity_consumed']:.2f} {consumption['unit']}", font=("Arial", 18, "bold"), bootstyle="danger").pack(anchor=W, pady=(0, 3))

            ttk.Label(card, text="Restante", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
            ttk.Label(card, text=f"{consumption['quantity_remaining']:.2f} {consumption['unit']}", font=("Arial", 18, "bold"), bootstyle="success").pack(anchor=W, pady=(0, 5))

            if total > 0:
                pct = (consumption['quantity_consumed'] / total) * 100
                ttk.Label(card, text=f"{pct:.1f}%", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
                ttk.Progressbar(card, value=pct, bootstyle="danger" if pct > 75 else "warning" if pct > 50 else "success").pack(fill=X)

            if consumption.get('notes'):
                txt = f"{consumption['notes'][:30]}..." if len(consumption['notes']) > 30 else consumption['notes']
                ttk.Label(card, text=txt, font=("Arial", 11, "italic"), bootstyle="secondary").pack(anchor=W, pady=(5, 0))
        else:
            ttk.Label(card, text="Sin consumo", font=("Arial", 14, "italic"), bootstyle="secondary").pack(anchor=W, pady=8)

    # ─── Crear periodos ───────────────────────────────────────────

    def _create_periods(self):
        purchases = self.supply_data['purchases']
        if len(purchases) < 1:
            return []

        periods = []
        for i in range(len(purchases)):
            if i + 1 < len(purchases):
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
                    'next_purchase': curr,
                    'consumption': consumption,
                    'is_current': i == 0
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
