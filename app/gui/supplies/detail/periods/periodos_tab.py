import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime


class periodsTab(ttk.Frame):
    """Tab de períodos: resumen de consumo actual + grid de cards paginado"""

    def __init__(self, parent, supply_data):
        super().__init__(parent)
        self.supply_data = supply_data
        self.consumption_expanded = False
        self.consumption_content_frame = None

        self.setup_ui()

    def setup_ui(self):
        # Resumen del período actual (collapsible)
        self._setup_consumption_collapsible()

        if not self.supply_data['purchases']:
            ttk.Label(self, text="No hay compras registradas para este insumo", font=("Arial", 10), bootstyle="secondary").pack(pady=20)
            return

        self.all_periods = self._create_periods()

        if not self.all_periods:
            ttk.Label(self, text="No hay suficientes compras para crear períodos", font=("Arial", 10), bootstyle="secondary").pack(pady=20)
            return

        self.periods_per_page = 4  # 2 columnas x 2 filas
        self.current_periods_page = 0
        self.total_periods_pages = (len(self.all_periods) + self.periods_per_page - 1) // self.periods_per_page

        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES)

        self.periods_scrolled = ScrolledFrame(main_container, autohide=True)
        self.periods_scrolled.pack(fill=BOTH, expand=YES)
        self.periods_cards_frame = self.periods_scrolled

        # Paginación
        pagination_frame = ttk.Frame(main_container)
        pagination_frame.pack(fill=X, pady=(10, 5))

        self.prev_btn = ttk.Button(pagination_frame, text="« Anterior", command=self._prev_page, bootstyle="secondary-outline", width=12)
        self.prev_btn.pack(side=LEFT, padx=5)

        self.page_label = ttk.Label(pagination_frame, text="", font=("Arial", 10))
        self.page_label.pack(side=LEFT, expand=YES)

        self.next_btn = ttk.Button(pagination_frame, text="Siguiente »", command=self._next_page, bootstyle="secondary-outline", width=12)
        self.next_btn.pack(side=RIGHT, padx=5)

        self._render_page()

    # ─── Consumption summary ──────────────────────────────────────

    def _setup_consumption_collapsible(self):
        if not self.supply_data['consumptions']:
            return

        frame = ttk.Frame(self)
        frame.pack(fill=X, pady=(0, 5))

        header = ttk.Frame(frame)
        header.pack(fill=X)

        self.collapse_icon = ttk.Label(header, text="▶", font=("Arial", 10), bootstyle="info", cursor="hand2")
        self.collapse_icon.pack(side=LEFT, padx=(0, 6))

        title = ttk.Label(header, text="Resumen del Período Actual", font=("Arial", 11, "bold"), bootstyle="info", cursor="hand2")
        title.pack(side=LEFT)

        for w in [header, self.collapse_icon, title]:
            w.bind('<Button-1>', lambda e: self._toggle_collapse())

        self.consumption_content_frame = ttk.Frame(frame)
        self._build_summary(self.consumption_content_frame)

    def _toggle_collapse(self):
        if self.consumption_expanded:
            self.consumption_content_frame.pack_forget()
            self.collapse_icon.configure(text="▶")
            self.consumption_expanded = False
        else:
            self.consumption_content_frame.pack(fill=X, pady=(5, 0))
            self.collapse_icon.configure(text="▼")
            self.consumption_expanded = True

    def _build_summary(self, parent):
        consumptions = self.supply_data['consumptions']
        if not consumptions:
            return

        current = consumptions[0]
        meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}

        start = self._to_date(current['start_date'])
        end = self._to_date(current['end_date'])

        start_str = f"{start.day}/{meses[start.month]}/{start.year}" if start else str(current['start_date'])
        end_str = f"{end.day}/{meses[end.month]}/{end.year}" if end else str(current['end_date'])

        card = ttk.Labelframe(parent, text=f" {start_str}  →  {end_str}", bootstyle="info", padding=10)
        card.pack(fill=X, pady=(0, 5))

        # Buscar compra del período
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

    # ─── Period cards grid ────────────────────────────────────────

    def _render_page(self):
        for w in self.periods_cards_frame.winfo_children():
            w.destroy()

        for col in range(2):
            self.periods_cards_frame.columnconfigure(col, weight=1, uniform="col")

        meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}

        start_idx = self.current_periods_page * self.periods_per_page
        end_idx = min(start_idx + self.periods_per_page, len(self.all_periods))

        for i, period in enumerate(self.all_periods[start_idx:end_idx]):
            self._create_card(self.periods_cards_frame, period, i // 2, i % 2, meses)

        self.page_label.configure(text=f"Página {self.current_periods_page + 1} de {self.total_periods_pages}")
        self.prev_btn.configure(state="normal" if self.current_periods_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_periods_page < self.total_periods_pages - 1 else "disabled")

    def _prev_page(self):
        if self.current_periods_page > 0:
            self.current_periods_page -= 1
            self._render_page()

    def _next_page(self):
        if self.current_periods_page < self.total_periods_pages - 1:
            self.current_periods_page += 1
            self._render_page()

    # ─── Period card ──────────────────────────────────────────────

    def _create_card(self, parent, period, row, col, meses):
        s = period['start_date']
        e = period['end_date']
        start_str = f"{s.day}/{meses[s.month]}/{s.year}"
        end_str = f"{e.day}/{meses[e.month]}/{e.year}"

        style = "success" if period['is_current'] else "info"
        card = ttk.Labelframe(parent, text=f" {start_str} - {end_str}" + (" (Actual)" if period['is_current'] else ""), bootstyle=style, padding=8)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        purchase = period['purchase']
        consumption = period['consumption']
        prev_stock = purchase.get('initial_stock', 0.0)

        if prev_stock > 0:
            ttk.Label(card, text="Sobró del periodo anterior", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
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

    # ─── Period data creation ─────────────────────────────────────

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

    # ─── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _to_date(value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        if hasattr(value, 'date') and callable(value.date):
            return value.date()
        if hasattr(value, 'year'):
            return value
        return None
