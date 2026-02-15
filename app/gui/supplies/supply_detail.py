import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime
from app.data.providers.supplies import supply_provider


class SupplyDetailView(ttk.Frame):
    """Vista de detalle de un insumo con su historial de compras y consumos"""

    def __init__(self, parent, app, supply_id, on_back_callback, on_edit_purchase_callback=None, on_tab_change_callback=None):
        super().__init__(parent)
        self.app = app
        self.supply_id = supply_id
        self.on_back_callback = on_back_callback
        self.on_edit_purchase_callback = on_edit_purchase_callback
        self.on_tab_change_callback = on_tab_change_callback
        self.provider = supply_provider
        self.supply_data = None
        self.consumption_expanded = False
        self.consumption_content_frame = None

        self.load_supply_data()
        self.setup_ui()

    def load_supply_data(self):
        """Load supply data with purchases and consumptions"""
        self.supply_data = self.provider.get_supply_by_id(self.supply_id)

    def setup_ui(self):
        """Setup the detail view UI"""
        if not self.supply_data:
            ttk.Label(
                self,
                text="Insumo no encontrado",
                font=("Arial", 14, "bold")
            ).pack(pady=50)
            return

        main_layout = ttk.Frame(self)
        main_layout.pack(fill=BOTH, expand=YES)

        # 1. Header compacto: [← Volver]  Nombre · Proveedor
        self.setup_header(main_layout)

        # 2. Tabs inmediatamente debajo del header
        self.setup_tabs(main_layout)

        # 3. Contenido del tab seleccionado
        self.tab_content_frame = ttk.Frame(main_layout)
        self.tab_content_frame.pack(fill=BOTH, expand=YES)

        # Mostrar tab por defecto
        self._show_historial_tab()

    def setup_header(self, parent):
        """Header compacto en una sola línea"""
        header = ttk.Frame(parent)
        header.pack(fill=X, pady=(0, 8))

        # Back button
        ttk.Button(
            header,
            text="← Volver",
            command=self.on_back_callback,
            bootstyle="secondary-outline",
            width=10
        ).pack(side=LEFT, padx=(0, 15))

        # Nombre del insumo (bold)
        ttk.Label(
            header,
            text=self.supply_data['supply_name'],
            font=("Arial", 16, "bold")
        ).pack(side=LEFT)

        # Separador visual
        ttk.Label(
            header,
            text="·",
            font=("Arial", 16),
            bootstyle="secondary"
        ).pack(side=LEFT, padx=10)

        # Proveedor
        ttk.Label(
            header,
            text=self.supply_data['supplier_name'],
            font=("Arial", 12),
            bootstyle="secondary"
        ).pack(side=LEFT)

    def setup_tabs(self, parent):
        """Tabs de navegación justo debajo del header"""
        ttk.Separator(parent, orient=HORIZONTAL).pack(fill=X, pady=(0, 8))

        tab_frame = ttk.Frame(parent)
        tab_frame.pack(fill=X, pady=(0, 8))

        self.current_tab = "historial"

        self.historial_btn = ttk.Button(
            tab_frame,
            text="Historial de Compras",
            command=lambda: self._switch_tab("historial"),
            bootstyle="primary",
            width=20
        )
        self.historial_btn.pack(side=LEFT, padx=(0, 5))

        self.periodos_btn = ttk.Button(
            tab_frame,
            text="Períodos",
            command=lambda: self._switch_tab("periodos"),
            bootstyle="secondary-outline",
            width=20
        )
        self.periodos_btn.pack(side=LEFT)

    # ─── Consumption summary (solo en tab Períodos) ───────────────

    def _setup_consumption_collapsible(self, parent):
        """Resumen compacto del período actual (collapsible), solo para tab períodos"""
        if not self.supply_data['consumptions']:
            return

        consumption_frame = ttk.Frame(parent)
        consumption_frame.pack(fill=X, pady=(0, 5))

        header_frame = ttk.Frame(consumption_frame)
        header_frame.pack(fill=X)

        self.collapse_icon = ttk.Label(
            header_frame,
            text="▶",
            font=("Arial", 10),
            bootstyle="info",
            cursor="hand2"
        )
        self.collapse_icon.pack(side=LEFT, padx=(0, 6))

        title_label = ttk.Label(
            header_frame,
            text="Resumen del Período Actual",
            font=("Arial", 11, "bold"),
            bootstyle="info",
            cursor="hand2"
        )
        title_label.pack(side=LEFT)

        for widget in [header_frame, self.collapse_icon, title_label]:
            widget.bind('<Button-1>', lambda e: self._toggle_consumption_collapse())

        self.consumption_content_frame = ttk.Frame(consumption_frame)
        self._build_consumption_summary(self.consumption_content_frame)

    def _toggle_consumption_collapse(self):
        """Toggle expand/collapse del resumen"""
        if self.consumption_expanded:
            self.consumption_content_frame.pack_forget()
            self.collapse_icon.configure(text="▶")
            self.consumption_expanded = False
        else:
            self.consumption_content_frame.pack(fill=X, pady=(5, 0))
            self.collapse_icon.configure(text="▼")
            self.consumption_expanded = True

    def _build_consumption_summary(self, parent):
        """Resumen compacto horizontal del período actual"""
        consumptions = self.supply_data['consumptions']
        if not consumptions:
            return

        current_consumption = consumptions[0]

        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        start = current_consumption['start_date']
        if isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()
        elif not hasattr(start, 'year'):
            start = None

        end = current_consumption['end_date']
        if isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()
        elif not hasattr(end, 'year'):
            end = None

        start_str = f"{start.day}/{meses[start.month]}/{start.year}" if start else str(current_consumption['start_date'])
        end_str = f"{end.day}/{meses[end.month]}/{end.year}" if end else str(current_consumption['end_date'])

        summary_card = ttk.Labelframe(
            parent,
            text=f" {start_str}  →  {end_str}",
            bootstyle="info",
            padding=10
        )
        summary_card.pack(fill=X, pady=(0, 5))

        period_purchase = None
        if start and self.supply_data['purchases']:
            for purchase in self.supply_data['purchases']:
                p_date = purchase['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
                elif not hasattr(p_date, 'year'):
                    continue
                if p_date <= start:
                    period_purchase = purchase
                    break

        kpi_frame = ttk.Frame(summary_card)
        kpi_frame.pack(fill=X)

        if period_purchase:
            self._create_kpi(kpi_frame, "Compra",
                           f"{period_purchase['quantity']:.2f} {period_purchase['unit']}",
                           "info", side=LEFT)

        self._create_kpi(kpi_frame, "Consumido",
                       f"{current_consumption['quantity_consumed']:.2f} {current_consumption['unit']}",
                       "danger", side=LEFT)

        self._create_kpi(kpi_frame, "Restante",
                       f"{current_consumption['quantity_remaining']:.2f} {current_consumption['unit']}",
                       "success", side=LEFT)

        latest_purchase = self.supply_data['purchases'][0] if self.supply_data['purchases'] else None
        inventory = current_consumption['quantity_remaining']
        if latest_purchase:
            inventory += latest_purchase['quantity']

        self._create_kpi(kpi_frame, "Inventario Disponible",
                       f"{inventory:.2f} {current_consumption['unit']}",
                       "primary", side=LEFT)

        if period_purchase and period_purchase['quantity'] > 0:
            prev_stock = period_purchase.get('initial_stock', 0.0)
            total_stock = prev_stock + period_purchase['quantity']
            if total_stock > 0:
                percent = (current_consumption['quantity_consumed'] / total_stock) * 100

                progress_frame = ttk.Frame(summary_card)
                progress_frame.pack(fill=X, pady=(8, 0))

                ttk.Label(
                    progress_frame,
                    text=f"Consumo: {percent:.1f}%",
                    font=("Arial", 9),
                    bootstyle="secondary"
                ).pack(side=LEFT, padx=(0, 10))

                progress = ttk.Progressbar(
                    progress_frame,
                    value=percent,
                    bootstyle="danger" if percent > 75 else "warning" if percent > 50 else "success"
                )
                progress.pack(side=LEFT, fill=X, expand=YES)

        if current_consumption['notes']:
            ttk.Label(
                summary_card,
                text=f"Nota: {current_consumption['notes']}",
                font=("Arial", 9, "italic"),
                bootstyle="secondary",
                wraplength=600
            ).pack(anchor=W, pady=(5, 0))

    def _create_kpi(self, parent, label, value, style, side=LEFT):
        """Crea un mini KPI inline"""
        kpi = ttk.Frame(parent)
        kpi.pack(side=side, fill=X, expand=YES, padx=(0, 15))

        ttk.Label(
            kpi,
            text=label,
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            kpi,
            text=value,
            font=("Arial", 12, "bold"),
            bootstyle=style
        ).pack(anchor=W)

    # ─── Tab switching ────────────────────────────────────────────

    def _switch_tab(self, tab_name):
        """Switch between historial and periodos tabs"""
        if tab_name == self.current_tab:
            return

        self.current_tab = tab_name

        # Notificar cambio de tab al contenedor padre
        if self.on_tab_change_callback:
            self.on_tab_change_callback(tab_name)

        if tab_name == "historial":
            self.historial_btn.configure(bootstyle="primary")
            self.periodos_btn.configure(bootstyle="secondary-outline")
            self._show_historial_tab()
        else:
            self.historial_btn.configure(bootstyle="secondary-outline")
            self.periodos_btn.configure(bootstyle="primary")
            self._show_periodos_tab()

    def _show_historial_tab(self):
        """Show the historial de compras table"""
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        if self.supply_data['purchases']:
            columns = [
                {"text": "Fecha", "stretch": False, "width": 100},
                {"text": "Proveedor", "stretch": False, "width": 120},
                {"text": "Cantidad", "stretch": False, "width": 80},
                {"text": "Unidad", "stretch": False, "width": 80},
                {"text": "Precio Unit.", "stretch": False, "width": 100},
                {"text": "Total", "stretch": False, "width": 100},
                {"text": "Notas", "stretch": True, "width": 150}
            ]

            table_frame = ttk.Frame(self.tab_content_frame)
            table_frame.pack(fill=BOTH, expand=YES)

            self.purchases_table = Tableview(
                master=table_frame,
                coldata=columns,
                rowdata=[],
                paginated=True,
                searchable=False,
                bootstyle=PRIMARY,
                pagesize=10,
                height=10
            )
            self.purchases_table.pack(fill=BOTH, expand=YES)

            self.purchases_table.view.bind('<ButtonRelease-1>', self._on_purchase_clicked)

            self.display_purchases()
        else:
            ttk.Label(
                self.tab_content_frame,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)

    def _show_periodos_tab(self):
        """Show the periodos view with consumption summary + cards grid"""
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        # Reset estado del collapsible
        self.consumption_expanded = False

        # Resumen del período actual (solo en esta tab)
        self._setup_consumption_collapsible(self.tab_content_frame)

        if not self.supply_data['purchases']:
            ttk.Label(
                self.tab_content_frame,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)
            return

        self.all_periods = self._create_periods()

        if not self.all_periods:
            ttk.Label(
                self.tab_content_frame,
                text="No hay suficientes compras para crear períodos",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)
            return

        self.periods_per_page = 4  # 2 columnas x 2 filas
        self.current_periods_page = 0
        self.total_periods_pages = (len(self.all_periods) + self.periods_per_page - 1) // self.periods_per_page

        main_container = ttk.Frame(self.tab_content_frame)
        main_container.pack(fill=BOTH, expand=YES)

        self.periods_scrolled = ScrolledFrame(main_container, autohide=True)
        self.periods_scrolled.pack(fill=BOTH, expand=YES)

        self.periods_cards_frame = self.periods_scrolled

        pagination_frame = ttk.Frame(main_container)
        pagination_frame.pack(fill=X, pady=(10, 5))

        self.prev_periods_btn = ttk.Button(
            pagination_frame,
            text="« Anterior",
            command=self._prev_periods_page,
            bootstyle="secondary-outline",
            width=12
        )
        self.prev_periods_btn.pack(side=LEFT, padx=5)

        self.periods_page_label = ttk.Label(
            pagination_frame,
            text="",
            font=("Arial", 10)
        )
        self.periods_page_label.pack(side=LEFT, expand=YES)

        self.next_periods_btn = ttk.Button(
            pagination_frame,
            text="Siguiente »",
            command=self._next_periods_page,
            bootstyle="secondary-outline",
            width=12
        )
        self.next_periods_btn.pack(side=RIGHT, padx=5)

        self._render_periods_page()

    def _render_periods_page(self):
        """Render the current page of periods"""
        for widget in self.periods_cards_frame.winfo_children():
            widget.destroy()

        for col in range(2):
            self.periods_cards_frame.columnconfigure(col, weight=1, uniform="col")

        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        start_idx = self.current_periods_page * self.periods_per_page
        end_idx = min(start_idx + self.periods_per_page, len(self.all_periods))

        for i, period in enumerate(self.all_periods[start_idx:end_idx]):
            row = i // 2
            col = i % 2
            self._create_period_card_grid(self.periods_cards_frame, period, row, col, meses)

        self.periods_page_label.configure(
            text=f"Página {self.current_periods_page + 1} de {self.total_periods_pages}"
        )
        self.prev_periods_btn.configure(
            state="normal" if self.current_periods_page > 0 else "disabled"
        )
        self.next_periods_btn.configure(
            state="normal" if self.current_periods_page < self.total_periods_pages - 1 else "disabled"
        )

    def _prev_periods_page(self):
        if self.current_periods_page > 0:
            self.current_periods_page -= 1
            self._render_periods_page()

    def _next_periods_page(self):
        if self.current_periods_page < self.total_periods_pages - 1:
            self.current_periods_page += 1
            self._render_periods_page()

    # ─── Periods creation ─────────────────────────────────────────

    def _create_periods(self):
        """Create periods based on purchase dates"""
        purchases = self.supply_data['purchases']
        if len(purchases) < 1:
            return []

        periods = []

        for i in range(len(purchases)):
            current_purchase = purchases[i]

            if i + 1 < len(purchases):
                previous_purchase = purchases[i + 1]

                current_date = current_purchase['purchase_date']
                if isinstance(current_date, str):
                    current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

                previous_date = previous_purchase['purchase_date']
                if isinstance(previous_date, str):
                    previous_date = datetime.strptime(previous_date, "%Y-%m-%d").date()

                consumption = None
                for cons in self.supply_data['consumptions']:
                    start = cons['start_date']
                    if isinstance(start, str):
                        start = datetime.strptime(start, "%Y-%m-%d").date()

                    end = cons['end_date']
                    if isinstance(end, str):
                        end = datetime.strptime(end, "%Y-%m-%d").date()

                    if start >= previous_date and end <= current_date:
                        consumption = cons
                        break
                    elif abs((start - previous_date).days) <= 2 and abs((end - current_date).days) <= 2:
                        consumption = cons
                        break

                periods.append({
                    'start_date': previous_date,
                    'end_date': current_date,
                    'purchase': previous_purchase,
                    'next_purchase': current_purchase,
                    'consumption': consumption,
                    'is_current': i == 0
                })

        return periods

    def _create_period_card_grid(self, parent, period, row, col, meses):
        """Create a compact detailed card for a period in grid layout"""
        start_str = f"{period['start_date'].day}/{meses[period['start_date'].month]}/{period['start_date'].year}"
        end_str = f"{period['end_date'].day}/{meses[period['end_date'].month]}/{period['end_date'].year}"

        card_style = "success" if period['is_current'] else "info"

        card = ttk.Labelframe(
            parent,
            text=f" {start_str} - {end_str}" + (" (Actual)" if period['is_current'] else ""),
            bootstyle=card_style,
            padding=8,
        )
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

        purchase = period['purchase']
        consumption = period['consumption']

        prev_initial_stock = purchase.get('initial_stock', 0.0)

        if prev_initial_stock > 0:
            ttk.Label(card, text="Sobró del periodo anterior", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
            ttk.Label(card, text=f"{prev_initial_stock:.2f} {purchase['unit']}", font=("Arial", 16, "bold"), bootstyle="secondary").pack(anchor=W, pady=(0, 3))

        ttk.Label(card, text="Compra", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
        ttk.Label(card, text=f"{purchase['quantity']:.2f} {purchase['unit']}", font=("Arial", 18, "bold"), bootstyle="info").pack(anchor=W)

        total_stock = prev_initial_stock + purchase['quantity']
        if prev_initial_stock > 0:
            ttk.Label(card, text=f"Total: {total_stock:.2f} {purchase['unit']}", font=("Arial", 11, "italic"), bootstyle="info").pack(anchor=W, pady=(0, 3))

        ttk.Separator(card, orient=HORIZONTAL).pack(fill=X, pady=3)

        if consumption:
            ttk.Label(card, text="Consumido", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
            ttk.Label(card, text=f"{consumption['quantity_consumed']:.2f} {consumption['unit']}", font=("Arial", 18, "bold"), bootstyle="danger").pack(anchor=W, pady=(0, 3))

            ttk.Label(card, text="Restante", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
            ttk.Label(card, text=f"{consumption['quantity_remaining']:.2f} {consumption['unit']}", font=("Arial", 18, "bold"), bootstyle="success").pack(anchor=W, pady=(0, 5))

            if total_stock > 0:
                percent_consumed = (consumption['quantity_consumed'] / total_stock) * 100
                ttk.Label(card, text=f"{percent_consumed:.1f}%", font=("Arial", 12), bootstyle="secondary").pack(anchor=W)
                progress = ttk.Progressbar(card, value=percent_consumed, bootstyle="danger" if percent_consumed > 75 else "warning" if percent_consumed > 50 else "success")
                progress.pack(fill=X)

            if consumption.get('notes'):
                ttk.Label(card, text=f"{consumption['notes'][:30]}..." if len(consumption['notes']) > 30 else consumption['notes'], font=("Arial", 11, "italic"), bootstyle="secondary").pack(anchor=W, pady=(5, 0))
        else:
            ttk.Label(card, text="Sin consumo", font=("Arial", 14, "italic"), bootstyle="secondary").pack(anchor=W, pady=8)

    # ─── Purchases table ──────────────────────────────────────────

    def display_purchases(self):
        """Fill purchases table with data"""
        self.purchases_table.delete_rows()

        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        rows = []
        for purchase in self.supply_data['purchases']:
            if hasattr(purchase['purchase_date'], 'strftime'):
                fecha = purchase['purchase_date']
                date_str = f"{fecha.day}/{meses[fecha.month]}/{fecha.year}"
            else:
                date_str = str(purchase['purchase_date'])

            rows.append([
                date_str,
                purchase.get('supplier_name', 'N/A'),
                f"{purchase['quantity']:.2f}",
                purchase['unit'],
                f"${purchase['unit_price']:.2f}",
                f"${purchase['total_price']:.2f}",
                purchase['notes'] or ""
            ])

        if rows:
            self.purchases_table.insert_rows(0, rows)

        self.purchases_table.load_table_data()

    def _on_purchase_clicked(self, event):
        """Handle click on purchase row - open edit form"""
        if not self.on_edit_purchase_callback:
            return

        item = self.purchases_table.view.identify_row(event.y)
        if not item:
            return

        self.purchases_table.view.selection_set(item)
        self._process_purchase_selection()

    def _process_purchase_selection(self):
        """Process the purchase selection"""
        if not self.on_edit_purchase_callback:
            return

        selected_items = self.purchases_table.view.selection()
        if not selected_items:
            return

        try:
            selected_iid = selected_items[0]
            row_values = self.purchases_table.view.item(selected_iid)['values']
            if not row_values:
                return

            date_str = row_values[0]

            meses_inv = {
                'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
            }

            partes = date_str.split('/')
            if len(partes) == 3:
                dia = int(partes[0])
                mes = meses_inv.get(partes[1], 1)
                anio = int(partes[2])
                purchase_date = datetime(anio, mes, dia).date()
            else:
                purchase_date = datetime.strptime(date_str, "%d/%m/%Y").date()

            selected_purchase = None
            for purchase in self.supply_data['purchases']:
                p_date = purchase['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
                elif hasattr(p_date, 'date'):
                    p_date = p_date.date()

                if p_date == purchase_date:
                    selected_purchase = purchase
                    break

            if selected_purchase and self.on_edit_purchase_callback:
                self.on_edit_purchase_callback(
                    self.supply_id,
                    self.supply_data['supply_name'],
                    selected_purchase
                )

        except Exception as e:
            print(f"Error selecting purchase for edit: {e}")

    def refresh(self):
        """Refresh the detail view"""
        self.load_supply_data()
        if self.supply_data and self.supply_data['purchases']:
            if self.current_tab == "historial" and hasattr(self, 'purchases_table'):
                self.display_purchases()
