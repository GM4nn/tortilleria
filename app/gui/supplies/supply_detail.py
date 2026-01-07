import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
from app.data.providers.supplies import supply_provider


class SupplyDetailView(ttk.Frame):
    """Vista de detalle de un insumo con su historial de compras y consumos"""

    def __init__(self, parent, app, supply_id, on_back_callback, on_new_purchase_callback, on_purchase_selected_callback=None):
        super().__init__(parent)
        self.app = app
        self.supply_id = supply_id
        self.on_back_callback = on_back_callback
        self.on_new_purchase_callback = on_new_purchase_callback
        self.on_purchase_selected_callback = on_purchase_selected_callback
        self.provider = supply_provider
        self.supply_data = None
        self.consumption_panel = None  # Panel derecho para mostrar consumo

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

        # Crear layout con dos columnas: contenido principal a la izquierda, panel de consumo a la derecha
        main_layout = ttk.Frame(self)
        main_layout.pack(fill=BOTH, expand=YES)

        # Columna izquierda: contenido principal
        left_column = ttk.Frame(main_layout)
        left_column.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Header con boton de regresar
        self.setup_header(left_column)

        # Informacion del insumo
        self.setup_supply_info(left_column)

        # Separador
        ttk.Separator(left_column, orient=HORIZONTAL).pack(fill=X, pady=15)

        # Periodo actual de consumo (si existe)
        if self.supply_data['consumptions']:
            self.setup_current_consumption_summary(left_column)

            # Separador
            ttk.Separator(left_column, orient=HORIZONTAL).pack(fill=X, pady=15)

        # Historial de compras
        self.setup_purchases_section(left_column)

        # Columna derecha: panel de consumo de compra seleccionada (inicialmente oculto)
        self.consumption_panel = ttk.Frame(main_layout, width=400)
        self.consumption_panel.pack_propagate(False)
        # No hacer pack() aquí, se mostrará solo cuando se seleccione una compra

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

    def setup_current_consumption_summary(self, parent):
        """Display current consumption period summary at the top"""
        consumption_frame = ttk.Frame(parent)
        consumption_frame.pack(fill=X, pady=(0, 10))

        # Titulo
        ttk.Label(
            consumption_frame,
            text="Periodo Actual de Consumo",
            font=("Arial", 14, "bold"),
            bootstyle="primary"
        ).pack(anchor=W, pady=(0, 10))

        # Mostrar resumen del consumo actual
        self.setup_consumption_summary(consumption_frame)

    def setup_purchases_section(self, parent):
        """Display purchases history"""
        purchases_frame = ttk.Frame(parent)
        purchases_frame.pack(fill=BOTH, expand=YES)

        # Header con titulo y boton de nueva compra
        header = ttk.Frame(purchases_frame)
        header.pack(fill=X, pady=(0, 10))

        ttk.Label(
            header,
            text="Historial de Compras",
            font=("Arial", 14, "bold"),
            bootstyle="primary"
        ).pack(side=LEFT)

        ttk.Button(
            header,
            text="+ Nueva Compra",
            command=self._new_purchase,
            bootstyle="success",
            width=20
        ).pack(side=RIGHT)

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

            table_frame = ttk.Frame(purchases_frame)
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

            # Bind click event para mostrar consumo de la compra en panel derecho
            self.purchases_table.view.bind('<<TreeviewSelect>>', self._on_purchase_selected)

            # Llenar tabla
            self.display_purchases()
        else:
            ttk.Label(
                purchases_frame,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)


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

        # Calcular restante total general
        total_remaining = current_consumption['quantity_remaining']

        # Sumar todas las compras que se hicieron en o después del end_date del consumo actual
        if end and self.supply_data['purchases']:
            for purchase in self.supply_data['purchases']:
                p_date = purchase['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
                elif not hasattr(p_date, 'year'):
                    continue

                # Si la compra es en o después del end_date del consumo actual, sumarla al restante total
                if p_date >= end:
                    total_remaining += purchase['quantity']

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
                    font=("Arial", 16, "bold"),
                    bootstyle="info"
                ).pack(anchor=W, pady=(0, 10))

                # Restante (Período)
                ttk.Label(
                    column1_frame,
                    text="Restante (Período)",
                    font=("Arial", 9),
                    bootstyle="secondary"
                ).pack(anchor=W)

                ttk.Label(
                    column1_frame,
                    text=f"{current_consumption['quantity_remaining']:.2f} {current_consumption['unit']}",
                    font=("Arial", 16, "bold"),
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
            font=("Arial", 16, "bold"),
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
                    font=("Arial", 16, "bold"),
                    bootstyle="warning"
                ).pack(anchor=W, pady=(0, 10))

        # COLUMNA 3: Restante Total
        column3_frame = ttk.Frame(stats_frame)
        column3_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        ttk.Label(
            column3_frame,
            text="Restante Total",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Label(
            column3_frame,
            text=f"{total_remaining:.2f} {current_consumption['unit']}",
            font=("Arial", 16, "bold"),
            bootstyle="primary"
        ).pack(anchor=W)

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
        # Ocultar el panel de consumo antes de abrir el formulario
        if self.consumption_panel and self.consumption_panel.winfo_exists():
            self.consumption_panel.pack_forget()

        if self.on_new_purchase_callback:
            self.on_new_purchase_callback(self.supply_id, self.supply_data['supply_name'])

    def _close_consumption_panel(self):
        """Close the consumption panel and deselect purchase"""
        # Deseleccionar la compra en la tabla
        if hasattr(self, 'purchases_table'):
            self.purchases_table.view.selection_remove(self.purchases_table.view.selection())

        # Ocultar el panel
        self.consumption_panel.pack_forget()

    def _on_purchase_selected(self, event):
        """Handle purchase row selection - show consumption for that purchase in right panel"""
        # Si hay un callback para notificar la selección de compra (para cerrar el formulario de compra)
        if self.on_purchase_selected_callback:
            self.on_purchase_selected_callback()

        # Get selected row
        selected_items = self.purchases_table.view.selection()
        if not selected_items:
            # Si no hay selección, ocultar el panel
            if self.consumption_panel and self.consumption_panel.winfo_exists():
                self.consumption_panel.pack_forget()
            return

        # Clear previous panel content
        if self.consumption_panel and self.consumption_panel.winfo_exists():
            for widget in self.consumption_panel.winfo_children():
                widget.destroy()

        # Mostrar el panel si está oculto
        if self.consumption_panel and not self.consumption_panel.winfo_ismapped():
            self.consumption_panel.pack(side=RIGHT, fill=BOTH, padx=(10, 0))
            # Forzar actualización del layout
            self.consumption_panel.update_idletasks()

        # Get the row index
        try:
            selected_iid = selected_items[0]
            row_values = self.purchases_table.view.item(selected_iid)['values']
            if not row_values:
                return

            # Parse the date from the selected row (formato: 12/Jun/2026)
            date_str = row_values[0]  # First column is the date
            # Second column is supplier name (we added it)

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

            # Find the purchase in our data and the previous purchase
            selected_purchase = None
            previous_purchase = None

            # Las compras están ordenadas por fecha descendente
            for i, purchase in enumerate(self.supply_data['purchases']):
                p_date = purchase['purchase_date'] if hasattr(purchase['purchase_date'], 'year') else purchase['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()

                if p_date == purchase_date:
                    selected_purchase = purchase
                    # La compra anterior es la siguiente en la lista (porque está ordenada desc)
                    if i + 1 < len(self.supply_data['purchases']):
                        previous_purchase = self.supply_data['purchases'][i + 1]
                    break

            if not selected_purchase:
                return

            # Buscar el consumo que corresponde a esta compra
            related_consumption = None
            if previous_purchase:
                prev_date = previous_purchase['purchase_date'] if hasattr(previous_purchase['purchase_date'], 'year') else previous_purchase['purchase_date']
                if isinstance(prev_date, str):
                    prev_date = datetime.strptime(prev_date, "%Y-%m-%d").date()

                # Buscar consumo entre la compra anterior y la actual
                for consumption in self.supply_data['consumptions']:
                    start = consumption['start_date'] if hasattr(consumption['start_date'], 'year') else consumption['start_date']
                    end = consumption['end_date'] if hasattr(consumption['end_date'], 'year') else consumption['end_date']

                    if isinstance(start, str):
                        start = datetime.strptime(start, "%Y-%m-%d").date()
                    if isinstance(end, str):
                        end = datetime.strptime(end, "%Y-%m-%d").date()

                    # El consumo debe estar en el rango entre las dos compras
                    if start >= prev_date and end <= purchase_date:
                        related_consumption = consumption
                        break
                    elif abs((start - prev_date).days) <= 2 and abs((end - purchase_date).days) <= 2:
                        related_consumption = consumption
                        break

            # Display the consumption info in right panel
            self._display_purchase_consumption(selected_purchase, previous_purchase, related_consumption)

        except Exception as e:
            print(f"Error selecting purchase: {e}")

    def _display_purchase_consumption(self, purchase, previous_purchase, consumption):
        """Display consumption info for selected purchase in right panel"""
        # Header del panel con titulo y boton cerrar
        header_panel = ttk.Frame(self.consumption_panel)
        header_panel.pack(fill=X, pady=(0, 10))

        # Titulo del panel con formato largo
        meses_completos = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
            7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        if hasattr(purchase['purchase_date'], 'strftime'):
            fecha = purchase['purchase_date']
            date_str = f"{fecha.day} de {meses_completos[fecha.month]} de {fecha.year}"
        else:
            date_str = str(purchase['purchase_date'])

        ttk.Label(
            header_panel,
            text=f"Compra del {date_str}",
            font=("Arial", 14, "bold"),
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

        # Informacion de la compra
        info_card = ttk.Labelframe(
            self.consumption_panel,
            text="  Informacion de Compra",
            bootstyle="primary",
            padding=15
        )
        info_card.pack(fill=X, pady=(0, 15))

        # Proveedor
        ttk.Label(
            info_card,
            text=f"Proveedor: {purchase.get('supplier_name', 'N/A')}",
            font=("Arial", 11, "bold"),
            bootstyle="info"
        ).pack(anchor=W, pady=3)

        # Detalles de la compra
        ttk.Label(
            info_card,
            text=f"Cantidad: {purchase['quantity']:.2f} {purchase['unit']}",
            font=("Arial", 11, "bold")
        ).pack(anchor=W, pady=3)

        ttk.Label(
            info_card,
            text=f"Precio unitario: ${purchase['unit_price']:.2f}",
            font=("Arial", 10)
        ).pack(anchor=W, pady=3)

        ttk.Label(
            info_card,
            text=f"Total: ${purchase['total_price']:.2f}",
            font=("Arial", 12, "bold"),
            bootstyle="success"
        ).pack(anchor=W, pady=3)

        if purchase['notes']:
            ttk.Label(
                info_card,
                text=f"Notas: {purchase['notes']}",
                font=("Arial", 9, "italic"),
                bootstyle="secondary",
                wraplength=350
            ).pack(anchor=W, pady=(8, 0))

        # Solo mostrar consumo si hay compra anterior
        if previous_purchase and consumption:

            # Formatear fecha de la compra para el título
            meses_completos = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }

            # Tarjeta de consumo
            consumption_card = ttk.Labelframe(
                self.consumption_panel,
                text=f"  Consumo Asociado",
                bootstyle="info",
                padding=15
            )
            consumption_card.pack(fill=X, pady=(0, 15))
 
            # Periodo de consumo con formato completo en letras
            if hasattr(consumption['start_date'], 'strftime'):
                start = consumption['start_date']
                start_str = f"{start.day} de {meses_completos[start.month]} de {start.year}"
            else:
                start_str = str(consumption['start_date'])

            if hasattr(consumption['end_date'], 'strftime'):
                end = consumption['end_date']
                end_str = f"{end.day} de {meses_completos[end.month]} de {end.year}"
            else:
                end_str = str(consumption['end_date'])

            ttk.Label(
                consumption_card,
                text=f"Periodo",
                font=("Arial", 9, "italic"),
                bootstyle="secondary"
            ).pack(anchor=W, pady=(0, 5))

            ttk.Label(
                consumption_card,
                text=f"del {start_str} \nhasta el {end_str}",
                font=("Arial", 12),
                bootstyle='info'
            ).pack(anchor=W, pady=(0, 15))

            # Información de la compra que se consumió (mostrar primero)
            if previous_purchase:

                # Formatear fecha de la compra inicial
                prev_date = previous_purchase['purchase_date']
                if isinstance(prev_date, str):
                    prev_date = datetime.strptime(prev_date, "%Y-%m-%d").date()
                elif not hasattr(prev_date, 'year'):
                    prev_date = None

                if prev_date:
                    prev_date_str = f"{prev_date.day} de {meses_completos[prev_date.month]} de {prev_date.year}"

                    # Título de la compra
                    ttk.Label(
                        consumption_card,
                        text=f"Compra del\n{prev_date_str}",
                        font=("Arial", 9),
                        bootstyle="secondary"
                    ).pack(anchor=W, pady=(0, 5))

                    # Total comprado
                    ttk.Label(
                        consumption_card,
                        text=f"{previous_purchase['quantity']:.2f} {previous_purchase['unit']}",
                        font=("Arial", 18, "bold"),
                        bootstyle='info'
                    ).pack(anchor=W, pady=(0, 15))

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


            # Calcular porcentaje consumido basado en la compra ANTERIOR (que es la que se consumió)
            total_purchased = previous_purchase['quantity'] if previous_purchase else purchase['quantity']
            if total_purchased > 0:
                percent_consumed = (consumption['quantity_consumed'] / total_purchased) * 100

                # Separador
                ttk.Separator(consumption_card, orient=HORIZONTAL).pack(fill=X, pady=10)

                # Barra de progreso
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

            # Notas si existen
            if consumption['notes']:
                ttk.Separator(consumption_card, orient=HORIZONTAL).pack(fill=X, pady=10)
                ttk.Label(
                    consumption_card,
                    text=f"Notas: {consumption['notes']}",
                    font=("Arial", 9, "italic"),
                    bootstyle="secondary",
                    wraplength=350
                ).pack(anchor=W)
        else:
            # No hay consumo asociado
            no_consumption_card = ttk.Labelframe(
                self.consumption_panel,
                text="  Consumo",
                bootstyle="secondary",
                padding=15
            )
            no_consumption_card.pack(fill=X)

            ttk.Label(
                no_consumption_card,
                text="No hay registro de consumo\npara esta compra",
                font=("Arial", 10),
                bootstyle="secondary",
                justify=CENTER
            ).pack(pady=20)

    def refresh(self):
        """Refresh the detail view"""
        self.load_supply_data()
        if self.supply_data and self.supply_data['purchases']:
            self.display_purchases()
