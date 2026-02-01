import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import datetime
from app.data.providers.supplies import supply_provider


class SupplyDetailView(ttk.Frame):
    """Vista de detalle de un insumo con su historial de compras y consumos"""

    def __init__(self, parent, app, supply_id, on_back_callback, on_new_purchase_callback, on_edit_purchase_callback=None, on_tab_change_callback=None):
        super().__init__(parent)
        self.app = app
        self.supply_id = supply_id
        self.on_back_callback = on_back_callback
        self.on_new_purchase_callback = on_new_purchase_callback
        self.on_edit_purchase_callback = on_edit_purchase_callback  # Callback para editar compra
        self.on_tab_change_callback = on_tab_change_callback  # Callback cuando se cambia de pestaña
        self.provider = supply_provider
        self.supply_data = None
        self.consumption_expanded = False  # Estado del collapse
        self.consumption_content_frame = None  # Frame del contenido colapsable

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

        # Contenido principal
        main_layout = ttk.Frame(self)
        main_layout.pack(fill=BOTH, expand=YES)

        # Header con boton de regresar
        self.setup_header(main_layout)

        # Informacion del insumo
        self.setup_supply_info(main_layout)

        # Periodo actual de consumo (collapsible, si existe)
        if self.supply_data['consumptions']:
            self.setup_current_consumption_collapsible(main_layout)
        # Historial de compras
        self.setup_purchases_section(main_layout)

    def setup_header(self, parent):
        """Setup header with back button"""
        header = ttk.Frame(parent)
        header.pack(fill=X, pady=(0, 15))

        ttk.Button(
            header,
            text="← Volver",
            command=self.on_back_callback,
            bootstyle="secondary-outline",
            width=12
        ).pack(side=LEFT)

        ttk.Label(
            header,
            text="Detalle del Insumo",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT, padx=(20, 0))

    def setup_supply_info(self, parent):
        """Display supply basic information"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=X, pady=(0, 10))

        # Titulo
        ttk.Label(
            info_frame,
            text="Informacion General",
            font=("Arial", 14, "bold"),
            bootstyle="primary"
        ).pack(anchor=W, pady=(0, 10))

        # Grid de informacion
        details_grid = ttk.Frame(info_frame)
        details_grid.pack(fill=X)

        # Nombre
        ttk.Label(
            details_grid,
            text="Nombre del Insumo:",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky=W, pady=5, padx=(0, 10))

        ttk.Label(
            details_grid,
            text=self.supply_data['supply_name'],
            font=("Arial", 10, "bold")
        ).grid(row=0, column=1, sticky=W, pady=5)

        # Proveedor
        ttk.Label(
            details_grid,
            text="Proveedor Principal:",
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky=W, pady=5, padx=(0, 10))

        ttk.Label(
            details_grid,
            text=self.supply_data['supplier_name'],
            font=("Arial", 10, "bold")
        ).grid(row=1, column=1, sticky=W, pady=5)

    def setup_current_consumption_collapsible(self, parent):
        """Display current consumption period summary with collapsible content"""
        consumption_frame = ttk.Frame(parent)
        consumption_frame.pack(fill=X, pady=(0, 10))

        # Header clickeable para expandir/colapsar
        header_frame = ttk.Frame(consumption_frame)
        header_frame.pack(fill=X)

        # Icono de flecha y titulo
        self.collapse_icon = ttk.Label(
            header_frame,
            text="▶",
            font=("Arial", 12),
            bootstyle="primary",
            cursor="hand2"
        )
        self.collapse_icon.pack(side=LEFT, padx=(0, 8))

        title_label = ttk.Label(
            header_frame,
            text="Periodo Actual de Consumo",
            font=("Arial", 14, "bold"),
            bootstyle="primary",
            cursor="hand2"
        )
        title_label.pack(side=LEFT)

        # Hacer clickeable el header
        header_frame.bind('<Button-1>', lambda e: self._toggle_consumption_collapse())
        self.collapse_icon.bind('<Button-1>', lambda e: self._toggle_consumption_collapse())
        title_label.bind('<Button-1>', lambda e: self._toggle_consumption_collapse())

        # Frame del contenido (inicialmente oculto)
        self.consumption_content_frame = ttk.Frame(consumption_frame)
        # No hacer pack() - empieza colapsado

        # Mostrar resumen del consumo actual dentro del frame colapsable
        self.setup_consumption_summary(self.consumption_content_frame)

    def _toggle_consumption_collapse(self):
        """Toggle the consumption section collapse state"""
        if self.consumption_expanded:
            # Colapsar
            self.consumption_content_frame.pack_forget()
            self.collapse_icon.configure(text="▶")
            self.consumption_expanded = False
        else:
            # Expandir
            self.consumption_content_frame.pack(fill=X, pady=(10, 0))
            self.collapse_icon.configure(text="▼")
            self.consumption_expanded = True

    def setup_purchases_section(self, parent):
        """Display purchases history with tabs"""
        purchases_frame = ttk.Frame(parent)
        purchases_frame.pack(fill=BOTH, expand=YES)

        # Header con boton de nueva compra
        header = ttk.Frame(purchases_frame)
        header.pack(fill=X, pady=(0, 10))

        ttk.Button(
            header,
            text="+ Nueva Compra",
            command=self._new_purchase,
            bootstyle="success",
            width=20
        ).pack(side=RIGHT)

        # Tabs para historial y periodos
        tab_buttons_frame = ttk.Frame(purchases_frame)
        tab_buttons_frame.pack(fill=X, pady=(5, 10))

        self.current_tab = "historial"  # Estado actual de la pestaña

        # Botones de tabs
        self.historial_btn = ttk.Button(
            tab_buttons_frame,
            text="Historial de Compras",
            command=lambda: self._switch_tab("historial"),
            bootstyle="primary",
            width=20
        )
        self.historial_btn.pack(side=LEFT, padx=(0, 5))

        self.periodos_btn = ttk.Button(
            tab_buttons_frame,
            text="Períodos",
            command=lambda: self._switch_tab("periodos"),
            bootstyle="secondary-outline",
            width=20
        )
        self.periodos_btn.pack(side=LEFT)

        # Container para el contenido de las tabs
        self.tab_content_frame = ttk.Frame(purchases_frame)
        self.tab_content_frame.pack(fill=BOTH, expand=YES)

        # Mostrar la tab de historial por defecto
        self._show_historial_tab()

    def _switch_tab(self, tab_name):
        """Switch between historial and periodos tabs"""
        if tab_name == self.current_tab:
            return

        self.current_tab = tab_name

        # Notificar cambio de pestaña (para cerrar el formulario de edición si está abierto)
        if self.on_tab_change_callback:
            self.on_tab_change_callback(tab_name)

        # Actualizar estilos de botones
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
        # Limpiar contenido anterior
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        # Tabla de compras
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

            # Bind click event para editar la compra seleccionada
            # Usar ButtonRelease-1 en lugar de TreeviewSelect para evitar el bug del primer click
            self.purchases_table.view.bind('<ButtonRelease-1>', self._on_purchase_clicked)

            # Llenar tabla
            self.display_purchases()
        else:
            ttk.Label(
                self.tab_content_frame,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)

    def _show_periodos_tab(self):
        """Show the periodos view with cards in a grid layout with pagination"""
        # Limpiar contenido anterior
        for widget in self.tab_content_frame.winfo_children():
            widget.destroy()

        if not self.supply_data['purchases']:
            ttk.Label(
                self.tab_content_frame,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)
            return

        # Crear períodos basados en las compras
        self.all_periods = self._create_periods()

        if not self.all_periods:
            ttk.Label(
                self.tab_content_frame,
                text="No hay suficientes compras para crear períodos",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)
            return

        # Configuración de paginación
        self.periods_per_page = 8  # 4 columnas x 2 filas
        self.current_periods_page = 0
        self.total_periods_pages = (len(self.all_periods) + self.periods_per_page - 1) // self.periods_per_page

        # Frame contenedor principal
        main_container = ttk.Frame(self.tab_content_frame)
        main_container.pack(fill=BOTH, expand=YES)

        # ScrolledFrame para los cards (con scroll vertical)
        self.periods_scrolled = ScrolledFrame(main_container, autohide=True)
        self.periods_scrolled.pack(fill=BOTH, expand=YES)

        # Frame para los cards (dentro del scrolled frame)
        self.periods_cards_frame = self.periods_scrolled

        # Frame para controles de paginación (fuera del scroll)
        pagination_frame = ttk.Frame(main_container)
        pagination_frame.pack(fill=X, pady=(10, 5))

        # Botón anterior
        self.prev_periods_btn = ttk.Button(
            pagination_frame,
            text="« Anterior",
            command=self._prev_periods_page,
            bootstyle="secondary-outline",
            width=12
        )
        self.prev_periods_btn.pack(side=LEFT, padx=5)

        # Label de página actual
        self.periods_page_label = ttk.Label(
            pagination_frame,
            text="",
            font=("Arial", 10)
        )
        self.periods_page_label.pack(side=LEFT, expand=YES)

        # Botón siguiente
        self.next_periods_btn = ttk.Button(
            pagination_frame,
            text="Siguiente »",
            command=self._next_periods_page,
            bootstyle="secondary-outline",
            width=12
        )
        self.next_periods_btn.pack(side=RIGHT, padx=5)

        # Mostrar primera página
        self._render_periods_page()

    def _render_periods_page(self):
        """Render the current page of periods"""
        # Limpiar cards anteriores
        for widget in self.periods_cards_frame.winfo_children():
            widget.destroy()

        # Configurar grid de 4 columnas
        for col in range(4):
            self.periods_cards_frame.columnconfigure(col, weight=1, uniform="col")

        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        # Calcular índices de inicio y fin
        start_idx = self.current_periods_page * self.periods_per_page
        end_idx = min(start_idx + self.periods_per_page, len(self.all_periods))

        # Crear cards para la página actual
        for i, period in enumerate(self.all_periods[start_idx:end_idx]):
            row = i // 4
            col = i % 4
            self._create_period_card_grid(self.periods_cards_frame, period, row, col, meses)

        # Actualizar controles de paginación
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
        """Go to previous page of periods"""
        if self.current_periods_page > 0:
            self.current_periods_page -= 1
            self._render_periods_page()

    def _next_periods_page(self):
        """Go to next page of periods"""
        if self.current_periods_page < self.total_periods_pages - 1:
            self.current_periods_page += 1
            self._render_periods_page()

    def _create_periods(self):
        """Create periods based on purchase dates"""
        purchases = self.supply_data['purchases']
        if len(purchases) < 1:
            return []

        periods = []

        # Las compras están ordenadas por fecha descendente
        for i in range(len(purchases)):
            current_purchase = purchases[i]

            # El período va desde la compra anterior hasta esta compra
            if i + 1 < len(purchases):
                previous_purchase = purchases[i + 1]

                # Normalizar fechas
                current_date = current_purchase['purchase_date']
                if isinstance(current_date, str):
                    current_date = datetime.strptime(current_date, "%Y-%m-%d").date()

                previous_date = previous_purchase['purchase_date']
                if isinstance(previous_date, str):
                    previous_date = datetime.strptime(previous_date, "%Y-%m-%d").date()

                # Buscar consumo asociado
                consumption = None
                for cons in self.supply_data['consumptions']:
                    start = cons['start_date']
                    if isinstance(start, str):
                        start = datetime.strptime(start, "%Y-%m-%d").date()

                    end = cons['end_date']
                    if isinstance(end, str):
                        end = datetime.strptime(end, "%Y-%m-%d").date()

                    # El consumo debe estar entre las dos compras
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
        # Formatear fechas
        start_str = f"{period['start_date'].day}/{meses[period['start_date'].month]}/{period['start_date'].year}"
        end_str = f"{period['end_date'].day}/{meses[period['end_date'].month]}/{period['end_date'].year}"

        # Estilo del card según si es el período actual
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

        # Buscar stock anterior (initial_stock de esta compra)
        prev_initial_stock = purchase.get('initial_stock', 0.0)


        # === SECCIÓN: Stock Anterior (si existe) ===
        if prev_initial_stock > 0:
            stock_label = "Sobró del periodo anterior"

            ttk.Label(
                card,
                text=stock_label,
                font=("Arial", 12),
                bootstyle="secondary"
            ).pack(anchor=W)

            ttk.Label(
                card,
                text=f"{prev_initial_stock:.2f} {purchase['unit']}",
                font=("Arial", 16, "bold"),
                bootstyle="secondary"
            ).pack(anchor=W, pady=(0, 3))

        # === SECCIÓN: Compra del Período ===
        ttk.Label(
            card,
            text=f"Compra",
            font=("Arial", 12),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            card,
            text=f"{purchase['quantity']:.2f} {purchase['unit']}",
            font=("Arial", 18, "bold"),
            bootstyle="info"
        ).pack(anchor=W)

        # Stock total disponible
        total_stock = prev_initial_stock + purchase['quantity']
        if prev_initial_stock > 0:
            ttk.Label(
                card,
                text=f"Total: {total_stock:.2f} {purchase['unit']}",
                font=("Arial", 11, "italic"),
                bootstyle="info"
            ).pack(anchor=W, pady=(0, 3))

        # Separador
        ttk.Separator(card, orient=HORIZONTAL).pack(fill=X, pady=3)

        if consumption:
            # === SECCIÓN: Consumido ===
            ttk.Label(
                card,
                text="Consumido",
                font=("Arial", 12),
                bootstyle="secondary"
            ).pack(anchor=W)

            ttk.Label(
                card,
                text=f"{consumption['quantity_consumed']:.2f} {consumption['unit']}",
                font=("Arial", 18, "bold"),
                bootstyle="danger"
            ).pack(anchor=W, pady=(0, 3))

            # === SECCIÓN: Restante ===
            ttk.Label(
                card,
                text="Restante",
                font=("Arial", 12),
                bootstyle="secondary"
            ).pack(anchor=W)

            ttk.Label(
                card,
                text=f"{consumption['quantity_remaining']:.2f} {consumption['unit']}",
                font=("Arial", 18, "bold"),
                bootstyle="success"
            ).pack(anchor=W, pady=(0, 5))

            # === SECCIÓN: Barra de Progreso ===
            if total_stock > 0:
                percent_consumed = (consumption['quantity_consumed'] / total_stock) * 100

                ttk.Label(
                    card,
                    text=f"{percent_consumed:.1f}%",
                    font=("Arial", 12),
                    bootstyle="secondary"
                ).pack(anchor=W)

                progress = ttk.Progressbar(
                    card,
                    value=percent_consumed,
                    bootstyle="danger" if percent_consumed > 75 else "warning" if percent_consumed > 50 else "success"
                )
                progress.pack(fill=X)

            # Notas si existen
            if consumption.get('notes'):
                ttk.Label(
                    card,
                    text=f"{consumption['notes'][:30]}..." if len(consumption['notes']) > 30 else consumption['notes'],
                    font=("Arial", 11, "italic"),
                    bootstyle="secondary"
                ).pack(anchor=W, pady=(5, 0))
        else:
            # Sin consumo registrado
            ttk.Label(
                card,
                text="Sin consumo",
                font=("Arial", 14, "italic"),
                bootstyle="secondary"
            ).pack(anchor=W, pady=8)

    def _create_period_card(self, parent, period, index, meses):
        """Create a card for a period"""
        # Formatear fechas
        start_str = f"{period['start_date'].day}/{meses[period['start_date'].month]}/{period['start_date'].year}"
        end_str = f"{period['end_date'].day}/{meses[period['end_date'].month]}/{period['end_date'].year}"

        # Estilo del card según si es el período actual
        card_style = "success" if period['is_current'] else "info"

        card = ttk.Labelframe(
            parent,
            text=f"  Del {start_str} al {end_str}" + (" (Actual)" if period['is_current'] else ""),
            bootstyle=card_style,
            padding=15
        )
        card.pack(fill=X, pady=(0, 15), padx=10)

        # Hacer el card clickeable
        card.bind('<Button-1>', lambda e: self._on_period_card_click(period))
        for child in card.winfo_children():
            child.bind('<Button-1>', lambda e: self._on_period_card_click(period))

        # Info resumida en una fila
        info_frame = ttk.Frame(card)
        info_frame.pack(fill=X)
        info_frame.bind('<Button-1>', lambda e: self._on_period_card_click(period))

        # Compra
        purchase_frame = ttk.Frame(info_frame)
        purchase_frame.pack(side=LEFT, padx=(0, 30))
        purchase_frame.bind('<Button-1>', lambda e: self._on_period_card_click(period))

        ttk.Label(
            purchase_frame,
            text="Compra",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            purchase_frame,
            text=f"{period['purchase']['quantity']:.2f} {period['purchase']['unit']}",
            font=("Arial", 14, "bold"),
            bootstyle="info"
        ).pack(anchor=W)

        # Consumido
        if period['consumption']:
            consumed_frame = ttk.Frame(info_frame)
            consumed_frame.pack(side=LEFT, padx=(0, 30))
            consumed_frame.bind('<Button-1>', lambda e: self._on_period_card_click(period))

            ttk.Label(
                consumed_frame,
                text="Consumido",
                font=("Arial", 9),
                bootstyle="secondary"
            ).pack(anchor=W)

            ttk.Label(
                consumed_frame,
                text=f"{period['consumption']['quantity_consumed']:.2f} {period['consumption']['unit']}",
                font=("Arial", 14, "bold"),
                bootstyle="danger"
            ).pack(anchor=W)

            # Restante
            remaining_frame = ttk.Frame(info_frame)
            remaining_frame.pack(side=LEFT)
            remaining_frame.bind('<Button-1>', lambda e: self._on_period_card_click(period))

            ttk.Label(
                remaining_frame,
                text="Restante",
                font=("Arial", 9),
                bootstyle="secondary"
            ).pack(anchor=W)

            ttk.Label(
                remaining_frame,
                text=f"{period['consumption']['quantity_remaining']:.2f} {period['consumption']['unit']}",
                font=("Arial", 14, "bold"),
                bootstyle="success"
            ).pack(anchor=W)
        else:
            ttk.Label(
                info_frame,
                text="Sin registro de consumo",
                font=("Arial", 10, "italic"),
                bootstyle="secondary"
            ).pack(side=LEFT)

    def _on_period_card_click(self, period):
        """Handle period card click - show consumption in right panel"""
        # Limpiar panel anterior
        if self.consumption_panel and self.consumption_panel.winfo_exists():
            for widget in self.consumption_panel.winfo_children():
                widget.destroy()

        # Mostrar el panel si está oculto
        if self.consumption_panel and not self.consumption_panel.winfo_ismapped():
            self.consumption_panel.pack(side=RIGHT, fill=BOTH, padx=(10, 0))
            self.consumption_panel.update_idletasks()

        # Mostrar solo el consumo (sin info de compra)
        self._display_period_consumption(period)

    def _display_period_consumption(self, period):
        """Display only consumption info for selected period in right panel"""
        # Header del panel
        header_panel = ttk.Frame(self.consumption_panel)
        header_panel.pack(fill=X, pady=(0, 10))

        meses_completos = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
            7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        start_str = f"{period['start_date'].day} de {meses_completos[period['start_date'].month]} de {period['start_date'].year}"
        end_str = f"{period['end_date'].day} de {meses_completos[period['end_date'].month]} de {period['end_date'].year}"

        ttk.Label(
            header_panel,
            text=f"Período del {start_str} al {end_str}",
            font=("Arial", 12, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        # Boton cerrar
        ttk.Button(
            header_panel,
            text="✕",
            command=self._close_consumption_panel,
            bootstyle="danger-outline",
            width=3
        ).pack(side=RIGHT)

        # Separador
        ttk.Separator(self.consumption_panel, orient=HORIZONTAL).pack(fill=X, pady=(0, 15))

        if not period['consumption']:
            # No hay consumo
            no_consumption_card = ttk.Labelframe(
                self.consumption_panel,
                text="  Consumo",
                bootstyle="secondary",
                padding=15
            )
            no_consumption_card.pack(fill=X)

            ttk.Label(
                no_consumption_card,
                text="No hay registro de consumo\npara este período",
                font=("Arial", 10),
                bootstyle="secondary",
                justify=CENTER
            ).pack(pady=20)
            return

        consumption = period['consumption']
        purchase = period['purchase']

        # Tarjeta de consumo
        consumption_card = ttk.Labelframe(
            self.consumption_panel,
            text="  Consumo Asociado",
            bootstyle="info",
            padding=15
        )
        consumption_card.pack(fill=X, pady=(0, 15))

        # Meses abreviados
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        # Stock anterior (si existe)
        prev_initial_stock = purchase.get('initial_stock', 0.0)
        if prev_initial_stock > 0:
            # Buscar la compra anterior para obtener su fecha
            prev_prev_purchase = None
            for i, p in enumerate(self.supply_data['purchases']):
                p_date = p['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
                if p_date == period['start_date']:
                    if i + 1 < len(self.supply_data['purchases']):
                        prev_prev_purchase = self.supply_data['purchases'][i + 1]
                    break

            # Formatear etiqueta
            if prev_prev_purchase:
                prev_prev_date = prev_prev_purchase['purchase_date']
                if isinstance(prev_prev_date, str):
                    prev_prev_date = datetime.strptime(prev_prev_date, "%Y-%m-%d").date()
                prev_prev_date_str = f"{prev_prev_date.day}/{meses[prev_prev_date.month]}/{prev_prev_date.year}"
                label_text = f"Sobró de {prev_prev_date_str}"
            else:
                label_text = "Sobró de compra anterior"

            ttk.Label(
                consumption_card,
                text=label_text,
                font=("Arial", 9),
                bootstyle="secondary"
            ).pack(anchor=W, pady=(0, 2))

            ttk.Label(
                consumption_card,
                text=f"{prev_initial_stock:.2f} {purchase['unit']}",
                font=("Arial", 12, "bold"),
                bootstyle="secondary"
            ).pack(anchor=W, pady=(0, 10))

        # Compra del período
        purchase_date_str = f"{period['start_date'].day} de {meses_completos[period['start_date'].month]} de {period['start_date'].year}"

        ttk.Label(
            consumption_card,
            text=f"Compra del {purchase_date_str}",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(0, 5))

        ttk.Label(
            consumption_card,
            text=f"{purchase['quantity']:.2f} {purchase['unit']}",
            font=("Arial", 18, "bold"),
            bootstyle='info'
        ).pack(anchor=W, pady=(0, 5))

        # Stock total disponible
        total_stock_available = prev_initial_stock + purchase['quantity']
        if prev_initial_stock > 0:
            ttk.Label(
                consumption_card,
                text=f"Stock Total Disponible: {total_stock_available:.2f} {purchase['unit']}",
                font=("Arial", 9, "italic"),
                bootstyle="info"
            ).pack(anchor=W, pady=(0, 15))
        else:
            ttk.Label(consumption_card, text="").pack(pady=(0, 10))

        # Consumido
        ttk.Label(
            consumption_card,
            text="Consumido",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            consumption_card,
            text=f"{consumption['quantity_consumed']:.2f} {consumption['unit']}",
            font=("Arial", 18, "bold"),
            bootstyle="danger"
        ).pack(anchor=W, pady=(2, 10))

        # Restante
        ttk.Label(
            consumption_card,
            text="Restante",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            consumption_card,
            text=f"{consumption['quantity_remaining']:.2f} {consumption['unit']}",
            font=("Arial", 18, "bold"),
            bootstyle="success"
        ).pack(anchor=W, pady=(2, 10))

        # Barra de progreso
        if total_stock_available > 0:
            percent_consumed = (consumption['quantity_consumed'] / total_stock_available) * 100

            ttk.Separator(consumption_card, orient=HORIZONTAL).pack(fill=X, pady=10)

            ttk.Label(
                consumption_card,
                text=f"Consumo: {percent_consumed:.1f}%",
                font=("Arial", 10, "bold"),
                bootstyle="secondary"
            ).pack(anchor=W, pady=(0, 5))

            progress = ttk.Progressbar(
                consumption_card,
                value=percent_consumed,
                bootstyle="danger" if percent_consumed > 75 else "warning" if percent_consumed > 50 else "success"
            )
            progress.pack(fill=X)

        # Notas
        if consumption['notes']:
            ttk.Separator(consumption_card, orient=HORIZONTAL).pack(fill=X, pady=10)
            ttk.Label(
                consumption_card,
                text=f"Notas: {consumption['notes']}",
                font=("Arial", 9, "italic"),
                bootstyle="secondary",
                wraplength=350
            ).pack(anchor=W)


    def setup_consumption_summary(self, parent):
        """Display summary of current consumption period"""
        consumptions = self.supply_data['consumptions']
        if not consumptions:
            return

        # Obtener el consumo mas reciente
        current_consumption = consumptions[0]

        # Fechas con formato legible
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        meses_completos = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
            7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        # Normalizar start_date
        start = current_consumption['start_date']
        if isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()
        elif not hasattr(start, 'year'):
            start = None

        # Normalizar end_date
        end = current_consumption['end_date']
        if isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()
        elif not hasattr(end, 'year'):
            end = None

        # Formatear fechas para mostrar
        if start:
            start_str = f"{start.day}/{meses[start.month]}/{start.year}"
        else:
            start_str = str(current_consumption['start_date'])

        if end:
            end_str = f"{end.day}/{meses[end.month]}/{end.year}"
        else:
            end_str = str(current_consumption['end_date'])

        summary_card = ttk.Labelframe(
            parent,
            text=f"Del {start_str} al {end_str}",
            bootstyle="info",
            padding=15
        )
        summary_card.pack(fill=X, pady=(0, 10))

        # Buscar la compra que inició este período (compra más reciente <= start_date)
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

        # Calcular el stock acumulativo actual (restante REAL)
        # Usar el método del provider que calcula automáticamente el stock actual
        total_remaining = self.provider.get_current_stock(self.supply_id)

        # Frame para las 3 columnas
        stats_frame = ttk.Frame(summary_card)
        stats_frame.pack(fill=X, pady=(10, 0))

        # COLUMNA 1: Compra del período + Restante (Período)
        if period_purchase:
            column1_frame = ttk.Frame(stats_frame)
            column1_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 20))

            # Formatear fecha de la compra
            p_date = period_purchase['purchase_date']
            if isinstance(p_date, str):
                p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
            elif not hasattr(p_date, 'year'):
                p_date = None

            if p_date:
                p_date_str = f"{p_date.day}/{meses[p_date.month]}/{p_date.year}"

                # Obtener stock anterior y compra previa para usarlo después
                prev_initial_stock = period_purchase.get('initial_stock', 0.0)
                prev_prev_purchase = None

                if prev_initial_stock > 0:
                    # Buscar la compra anterior para obtener su fecha
                    purchases = self.supply_data['purchases']
                    for i, p in enumerate(purchases):
                        if p['id'] == period_purchase['id'] and i + 1 < len(purchases):
                            prev_prev_purchase = purchases[i + 1]
                            break

                # Compra del período
                ttk.Label(
                    column1_frame,
                    text=f"Compra ({p_date_str})",
                    font=("Arial", 9),
                    bootstyle="secondary"
                ).pack(anchor=W)

                ttk.Label(
                    column1_frame,
                    text=f"{period_purchase['quantity']:.2f} {period_purchase['unit']}",
                    font=("Arial", 12, "bold"),
                    bootstyle="info"
                ).pack(anchor=W, pady=(0, 2))

                # Stock disponible en esta fecha (stock anterior + compra de este día)
                stock_at_this_date = prev_initial_stock + period_purchase['quantity']

                # Construir el texto del stock con el desglose
                if prev_initial_stock > 0:
                    # Obtener la fecha de donde vino el stock
                    if prev_prev_purchase:
                        prev_prev_date_obj = prev_prev_purchase['purchase_date']
                        prev_prev_date_formatted = f"{prev_prev_date_obj.day}/{meses[prev_prev_date_obj.month]}/{prev_prev_date_obj.year}"
                        stock_text = f"+ {prev_initial_stock:.2f} que SOBRÓ de {prev_prev_date_formatted} = {stock_at_this_date:.2f} {period_purchase['unit']}"
                    else:
                        stock_text = f"+ {prev_initial_stock:.2f} que SOBRÓ = {stock_at_this_date:.2f} {period_purchase['unit']}"
                else:
                    stock_text = f"= {stock_at_this_date:.2f} {period_purchase['unit']}"

                ttk.Label(
                    column1_frame,
                    text=stock_text,
                    font=("Arial", 8, "italic"),
                    bootstyle="info"
                ).pack(anchor=W, pady=(0, 10))

                # Restante - mostrar con el rango de fechas del período
                # Formatear las fechas start y end
                start_str = f"{start.day}/{meses[start.month]}/{start.year}"
                end_str = f"{end.day}/{meses[end.month]}/{end.year}"

                ttk.Label(
                    column1_frame,
                    text=f"Restante del:\n{start_str} hasta {end_str}",
                    font=("Arial", 9),
                    bootstyle="secondary"
                ).pack(anchor=W)

                ttk.Label(
                    column1_frame,
                    text=f"{current_consumption['quantity_remaining']:.2f} {current_consumption['unit']}",
                    font=("Arial", 12, "bold"),
                    bootstyle="success"
                ).pack(anchor=W)

        # COLUMNA 2: Compra Actual + Consumido
        column2_frame = ttk.Frame(stats_frame)
        column2_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 20))

        # Consumido
        ttk.Label(
            column2_frame,
            text="Consumido",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            column2_frame,
            text=f"{current_consumption['quantity_consumed']:.2f} {current_consumption['unit']}",
            font=("Arial", 12, "bold"),
            bootstyle="danger"
        ).pack(anchor=W)

        # Compra Actual (la más reciente)
        latest_purchase = None
        if self.supply_data['purchases']:
            latest_purchase = self.supply_data['purchases'][0]

        if latest_purchase:
            latest_date = latest_purchase['purchase_date']
            if isinstance(latest_date, str):
                latest_date = datetime.strptime(latest_date, "%Y-%m-%d").date()
            elif not hasattr(latest_date, 'year'):
                latest_date = None

            if latest_date:
                latest_date_str = f"{latest_date.day}/{meses[latest_date.month]}/{latest_date.year}"

                ttk.Label(
                    column2_frame,
                    text=f"Compra Actual ({latest_date_str})",
                    font=("Arial", 9),
                    bootstyle="secondary"
                ).pack(anchor=W, pady=(10, 0))

                ttk.Label(
                    column2_frame,
                    text=f"{latest_purchase['quantity']:.2f} {latest_purchase['unit']}",
                    font=("Arial", 12, "bold"),
                    bootstyle="warning"
                ).pack(anchor=W, pady=(0, 10))

        # COLUMNA 3: Inventario Disponible
        column3_frame = ttk.Frame(stats_frame)
        column3_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        ttk.Label(
            column3_frame,
            text="Inventario Disponible",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        # Calcular inventario disponible TOTAL: restante del período + compra más reciente
        inventory_available = current_consumption['quantity_remaining']
        if latest_purchase:
            inventory_available += latest_purchase['quantity']

        ttk.Label(
            column3_frame,
            text=f"{inventory_available:.2f} {current_consumption['unit']}",
            font=("Arial", 12, "bold"),
            bootstyle="primary"
        ).pack(anchor=W)

        # Explicación
        ttk.Label(
            column3_frame,
            text="(Lo que tienes ahora)",
            font=("Arial", 8, "italic"),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(2, 0))

        # Barra de progreso
        if period_purchase:
            total_purchased = period_purchase['quantity']
            if total_purchased > 0:
                percent_consumed = (current_consumption['quantity_consumed'] / total_purchased) * 100

                # Separador
                ttk.Separator(summary_card, orient=HORIZONTAL).pack(fill=X, pady=10)

                # Barra de progreso
                ttk.Label(
                    summary_card,
                    text=f"Progreso de consumo: {percent_consumed:.1f}%",
                    font=("Arial", 9),
                    bootstyle="secondary"
                ).pack(anchor=W, pady=(0, 5))

                progress = ttk.Progressbar(
                    summary_card,
                    value=percent_consumed,
                    bootstyle="danger" if percent_consumed > 75 else "warning" if percent_consumed > 50 else "success",
                    length=400
                )
                progress.pack(fill=X)


        # Notas si existen
        if current_consumption['notes']:
            ttk.Label(
                summary_card,
                text=f"Nota: {current_consumption['notes']}",
                font=("Arial", 9, "italic"),
                bootstyle="secondary",
                wraplength=600
            ).pack(anchor=W, pady=(10, 0))

    def display_purchases(self):
        """Fill purchases table with data"""
        self.purchases_table.delete_rows()

        # Mapeo de meses en español
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        rows = []
        for purchase in self.supply_data['purchases']:
            if hasattr(purchase['purchase_date'], 'strftime'):
                # Formato: 12/Jun/2026
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

    def _new_purchase(self):
        """Handle new purchase button click"""
        if self.on_new_purchase_callback:
            self.on_new_purchase_callback(self.supply_id, self.supply_data['supply_name'])

    def _on_purchase_clicked(self, event):
        """Handle click on purchase row - open edit form"""
        # Ignorar si no hay callback configurado
        if not self.on_edit_purchase_callback:
            return

        # Identificar el item bajo el cursor
        item = self.purchases_table.view.identify_row(event.y)
        if not item:
            return

        # Seleccionar el item clickeado
        self.purchases_table.view.selection_set(item)

        # Procesar la selección
        self._process_purchase_selection()

    def _process_purchase_selection(self):
        """Process the purchase selection after a small delay"""
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

            # Parse the date from the selected row (formato: 12/Jun/2026)
            date_str = row_values[0]  # First column is the date

            # Mapeo inverso de meses
            meses_inv = {
                'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
            }

            # Parsear formato 12/Jun/2026
            partes = date_str.split('/')
            if len(partes) == 3:
                dia = int(partes[0])
                mes = meses_inv.get(partes[1], 1)
                anio = int(partes[2])
                purchase_date = datetime(anio, mes, dia).date()
            else:
                # Fallback a formato antiguo
                purchase_date = datetime.strptime(date_str, "%d/%m/%Y").date()

            # Find the purchase in our data
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
            self.display_purchases()
