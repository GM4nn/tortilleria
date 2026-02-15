import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, date
from app.constants import mexico_now
from app.data.providers.supplies import supply_provider


class PurchaseForm(ttk.Frame):
    """Formulario para registrar compras de insumos con validación de consumo"""

    def __init__(self, parent, app, on_close_callback):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = supply_provider
        self.on_close_callback = on_close_callback
        self.supply_id = None
        self.supply_name = None
        self.suggested_supplier_id = None  # Proveedor sugerido del insumo
        self.is_first_purchase = True
        self.suppliers_dict = {}  # Diccionario para mapear nombres a IDs
        self.edit_mode = False  # Modo edición
        self.purchase_id = None  # ID de la compra a editar

        self.setup_ui()

    def setup_ui(self):
        """Setup the form UI"""
        # Header with title and close button
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 20), padx=20)

        self.title_label = ttk.Label(
            header_frame,
            text="Registrar Compra de Insumo",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(side=LEFT)

        ttk.Button(
            header_frame,
            text="✕",
            command=self.on_close_callback,
            bootstyle="danger-outline",
            width=3
        ).pack(side=RIGHT)

        # Canvas y scrollbar para el formulario
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=BOTH, expand=YES, padx=20)

        import tkinter as tk
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)

        # Frame scrollable dentro del canvas
        form_container = ttk.Frame(self.canvas)

        # Configurar canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetar canvas y scrollbar
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Crear ventana en el canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=form_container, anchor="nw")

        # Actualizar región de scroll cuando cambie el tamaño
        form_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Ajustar ancho del frame al canvas
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Insumo (readonly)
        ttk.Label(form_container, text="Insumo:*").pack(anchor=W, pady=(5, 2))
        self.supply_label = ttk.Label(
            form_container,
            text="",
            font=("Arial", 11, "bold"),
            bootstyle="info"
        )
        self.supply_label.pack(anchor=W, pady=(0, 10))

        # Proveedor
        ttk.Label(form_container, text="Proveedor:*").pack(anchor=W, pady=(5, 2))
        self.supplier_var = ttk.StringVar()
        self.supplier_combo = ttk.Combobox(
            form_container,
            textvariable=self.supplier_var,
            values=[],
            width=28,
            state="readonly"
        )
        self.supplier_combo.pack(fill=X, pady=(0, 10))

        # Cargar proveedores
        self._load_suppliers()

        # Fecha de compra
        ttk.Label(form_container, text="Fecha de Compra:*").pack(anchor=W, pady=(5, 2))
        self.date_entry = ttk.DateEntry(
            form_container,
            bootstyle="primary",
            width=30,
            dateformat="%d/%m/%Y"
        )
        self.date_entry.pack(fill=X, pady=(0, 10))
        # Fix: reposicionar calendario a la izquierda para que no se corte
        self._patch_date_entry_position()

        # Unidad
        ttk.Label(form_container, text="Unidad:*").pack(anchor=W, pady=(5, 2))
        self.unit_var = ttk.StringVar()
        self.unit_combo = ttk.Combobox(
            form_container,
            textvariable=self.unit_var,
            values=["kilos", "litros", "piezas", "costales", "bultos", "cajas"],
            width=28
        )
        self.unit_combo.pack(fill=X, pady=(0, 10))

        # Cantidad
        ttk.Label(form_container, text="Cantidad:*").pack(anchor=W, pady=(5, 2))
        self.quantity_var = ttk.StringVar()
        self.quantity_entry = ttk.Entry(
            form_container,
            textvariable=self.quantity_var,
            width=30
        )
        self.quantity_entry.pack(fill=X, pady=(0, 10))
        self.quantity_entry.bind('<KeyRelease>', self.calculate_total)

        # Precio unitario
        ttk.Label(form_container, text="Precio Unitario ($):*").pack(anchor=W, pady=(5, 2))
        self.unit_price_var = ttk.StringVar()
        self.unit_price_entry = ttk.Entry(
            form_container,
            textvariable=self.unit_price_var,
            width=30
        )
        self.unit_price_entry.pack(fill=X, pady=(0, 10))
        self.unit_price_entry.bind('<KeyRelease>', self.calculate_total)

        # Total
        ttk.Label(form_container, text="Total ($):").pack(anchor=W, pady=(5, 2))
        self.total_var = ttk.StringVar()
        self.total_entry = ttk.Entry(
            form_container,
            textvariable=self.total_var,
            width=30,
            state=READONLY
        )
        self.total_entry.pack(fill=X, pady=(0, 10))

        # Notas
        ttk.Label(form_container, text="Notas:").pack(anchor=W, pady=(5, 2))
        self.notes_text = ttk.Text(
            form_container,
            height=3,
            width=30
        )
        self.notes_text.pack(fill=X, pady=(0, 10))

        # Frame para consumo (se mostrará si no es la primera compra)
        self.consumption_frame = ttk.Frame(form_container)

        ttk.Label(
            self.consumption_frame,
            text="Registrar Consumo del Período",
            font=("Arial", 12, "bold"),
            bootstyle="warning"
        ).pack(anchor=W, pady=(5, 5))

        ttk.Label(
            self.consumption_frame,
            text="¿Cuánto gastaste desde la última compra?",
            font=("Arial", 9, "italic"),
            bootstyle="secondary"
        ).pack(anchor=W, pady=(0, 10))

        # Información de última compra
        ttk.Label(self.consumption_frame, text="Última Compra:").pack(anchor=W, pady=(5, 2))

        # Frame para mostrar fecha y cantidad de última compra
        last_purchase_info_frame = ttk.Frame(self.consumption_frame)
        last_purchase_info_frame.pack(fill=X, pady=(0, 10))

        self.last_purchase_date_label = ttk.Label(
            last_purchase_info_frame,
            text="",
            font=("Arial", 10, "bold")
        )
        self.last_purchase_date_label.pack(side=LEFT)

        self.last_purchase_quantity_label = ttk.Label(
            last_purchase_info_frame,
            text="",
            font=("Arial", 10, "bold"),
            bootstyle="info"
        )
        self.last_purchase_quantity_label.pack(side=LEFT, padx=(10, 0))

        # Mostrar stock acumulado antes de la última compra
        self.previous_stock_title_label = ttk.Label(
            self.consumption_frame,
            text="",  # Se llenará dinámicamente
            font=("Arial", 10)
        )
        self.previous_stock_title_label.pack(anchor=W, pady=(5, 2))

        self.previous_stock_label = ttk.Label(
            self.consumption_frame,
            text="",
            font=("Arial", 10, "bold"),
            bootstyle="secondary"
        )
        self.previous_stock_label.pack(anchor=W, pady=(0, 5))

        # Resumen visual del total disponible
        self.total_available_frame = ttk.Labelframe(
            self.consumption_frame,
            text="  Total Disponible en el Período  ",
            bootstyle="info",
            padding=10
        )
        self.total_available_frame.pack(fill=X, pady=(5, 15))

        self.total_available_label = ttk.Label(
            self.total_available_frame,
            text="",
            font=("Arial", 14, "bold"),
            bootstyle="info"
        )
        self.total_available_label.pack()

        self.breakdown_label = ttk.Label(
            self.total_available_frame,
            text="",
            font=("Arial", 8, "italic"),
            bootstyle="secondary"
        )
        self.breakdown_label.pack(pady=(2, 0))

        # Cantidad consumida
        consumed_label_frame = ttk.Frame(self.consumption_frame)
        consumed_label_frame.pack(fill=X, pady=(5, 2))

        ttk.Label(consumed_label_frame, text="¿Cuánto Gastaste?*", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(consumed_label_frame, text="(puede incluir lo sobrante)", font=("Arial", 8, "italic"), bootstyle="secondary").pack(side=LEFT, padx=(5, 0))

        self.consumed_var = ttk.StringVar()
        self.consumed_entry = ttk.Entry(
            self.consumption_frame,
            textvariable=self.consumed_var,
            width=30,
            font=("Arial", 11)
        )
        self.consumed_entry.pack(fill=X, pady=(0, 10))

        # Cantidad restante
        remaining_label_frame = ttk.Frame(self.consumption_frame)
        remaining_label_frame.pack(fill=X, pady=(5, 2))

        ttk.Label(remaining_label_frame, text="¿Cuánto Sobró?*", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(remaining_label_frame, text="(lo que no usaste)", font=("Arial", 8, "italic"), bootstyle="secondary").pack(side=LEFT, padx=(5, 0))

        self.remaining_var = ttk.StringVar()
        self.remaining_entry = ttk.Entry(
            self.consumption_frame,
            textvariable=self.remaining_var,
            width=30,
            font=("Arial", 11)
        )
        self.remaining_entry.pack(fill=X, pady=(0, 5))

        # Validación visual en tiempo real
        self.validation_frame = ttk.Frame(self.consumption_frame)
        self.validation_frame.pack(fill=X, pady=(0, 10))

        self.validation_label = ttk.Label(
            self.validation_frame,
            text="",
            font=("Arial", 9),
            bootstyle="secondary"
        )
        self.validation_label.pack(anchor=W)

        # Bind para validación en tiempo real
        self.consumed_var.trace_add('write', self._validate_consumption_real_time)
        self.remaining_var.trace_add('write', self._validate_consumption_real_time)

        # Notas de consumo
        ttk.Label(self.consumption_frame, text="Notas de Consumo:").pack(anchor=W, pady=(5, 2))
        self.consumption_notes_text = ttk.Text(
            self.consumption_frame,
            height=2,
            width=30
        )
        self.consumption_notes_text.pack(fill=X, pady=(0, 10))

        # Botones fijos al fondo (fuera del canvas scrollable)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=(10, 0), padx=20, side=BOTTOM)

        self.save_btn = ttk.Button(
            btn_frame,
            text="Guardar",
            command=self.save_purchase,
            bootstyle="success",
            width=15
        )
        self.save_btn.pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.on_close_callback,
            bootstyle="secondary",
            width=15
        ).pack(side=LEFT)

    def _patch_date_entry_position(self):
        """Override DateEntry calendar popup to open to the left instead of right"""
        original_on_date_ask = self.date_entry._on_date_ask

        def _on_date_ask_fixed():
            from ttkbootstrap.dialogs import DatePickerDialog

            # Monkey-patch _set_window_position to open left-aligned
            original_set_pos = DatePickerDialog._set_window_position

            def _set_pos_left(dialog_self):
                if dialog_self.parent:
                    popup_width = dialog_self.root.winfo_reqwidth() or 226
                    xpos = dialog_self.parent.winfo_rootx() - popup_width
                    ypos = dialog_self.parent.winfo_rooty() + dialog_self.parent.winfo_height()
                    # Asegurar que no se salga por la izquierda
                    if xpos < 0:
                        xpos = 0
                    dialog_self.root.geometry(f"+{xpos}+{ypos}")
                else:
                    original_set_pos(dialog_self)

            DatePickerDialog._set_window_position = _set_pos_left
            try:
                original_on_date_ask()
            finally:
                DatePickerDialog._set_window_position = original_set_pos

        self.date_entry.button.configure(command=_on_date_ask_fixed)

    def _load_suppliers(self):
        """Load suppliers into combobox"""
        suppliers = self.provider.get_suppliers_list()
        self.suppliers_dict = {name: id for id, name in suppliers}
        supplier_names = list(self.suppliers_dict.keys())
        self.supplier_combo['values'] = supplier_names

    def set_supply(self, supply_id, supply_name, suggested_supplier_id=None):
        """Set the supply for this purchase"""
        self.supply_id = supply_id
        self.supply_name = supply_name
        self.suggested_supplier_id = suggested_supplier_id
        self.supply_label.configure(text=supply_name)
        self.last_purchase_data = None  # Guardar datos de última compra para validación

        # Pre-seleccionar el proveedor sugerido si está disponible
        if suggested_supplier_id:
            for name, id in self.suppliers_dict.items():
                if id == suggested_supplier_id:
                    self.supplier_var.set(name)
                    break

        # Verificar si tiene compras previas
        self.is_first_purchase = not self.provider.has_previous_purchases(supply_id)

        # Mostrar/ocultar frame de consumo
        if not self.is_first_purchase:
            # Obtener la última compra
            purchases = self.provider.get_purchases_by_supply(supply_id)
            if purchases:
                last_purchase = purchases[0]  # Ya están ordenadas por fecha desc
                self.last_purchase_data = last_purchase  # Guardar para validación

                last_date = last_purchase['purchase_date']
                if isinstance(last_date, str):
                    last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
                elif isinstance(last_date, datetime):
                    last_date = last_date.date()

                # Mostrar fecha
                self.last_purchase_date_label.configure(text=last_date.strftime("%d/%m/%Y"))

                # Mostrar cantidad y unidad de la última compra
                quantity_text = f"({last_purchase['quantity']:.2f} {last_purchase['unit']})"
                self.last_purchase_quantity_label.configure(text=quantity_text)

                # Mostrar stock anterior a la última compra SOLO si es mayor a 0
                previous_stock = last_purchase.get('initial_stock', 0.0)

                if previous_stock > 0:
                    # Solo mostrar si hay stock anterior
                    previous_stock_text = f"{previous_stock:.2f} {last_purchase['unit']}"
                    self.previous_stock_label.configure(text=previous_stock_text)

                    # Buscar la compra anterior para mostrar su fecha
                    purchases = self.provider.get_purchases_by_supply(supply_id)
                    if len(purchases) >= 2:
                        # Hay al menos 2 compras, la segunda es la anterior
                        prev_prev_purchase = purchases[1]
                        prev_prev_date = prev_prev_purchase['purchase_date']
                        if isinstance(prev_prev_date, str):
                            prev_prev_date = datetime.strptime(prev_prev_date, "%Y-%m-%d").date()
                        elif isinstance(prev_prev_date, datetime):
                            prev_prev_date = prev_prev_date.date()

                        title_text = f"Sobró de {prev_prev_date.strftime('%d/%m/%Y')}:"
                    else:
                        title_text = "Sobró de compra anterior:"

                    self.previous_stock_title_label.configure(text=title_text)
                else:
                    # Ocultar los labels si no hay stock anterior
                    self.previous_stock_title_label.configure(text="")
                    self.previous_stock_label.configure(text="")

                # Calcular y mostrar total disponible
                total_available = previous_stock + last_purchase['quantity']
                self.total_available_label.configure(
                    text=f"{total_available:.2f} {last_purchase['unit']}"
                )

                # Mostrar el desglose
                if previous_stock > 0:
                    breakdown_text = f"({previous_stock:.2f} sobrantes + {last_purchase['quantity']:.2f} comprados)"
                else:
                    breakdown_text = f"(Solo los {last_purchase['quantity']:.2f} comprados)"
                self.breakdown_label.configure(text=breakdown_text)

                self.consumption_frame.pack(fill=X, pady=(10, 0))
        else:
            self.consumption_frame.pack_forget()

        # Establecer fecha de hoy por defecto (formato dd/mm/yyyy)
        self.date_entry.entry.delete(0, END)
        self.date_entry.entry.insert(0, mexico_now().strftime("%d/%m/%Y"))

    def calculate_total(self, event=None):
        """Calculate total price"""
        try:
            quantity = float(self.quantity_var.get() or 0)
            unit_price = float(self.unit_price_var.get() or 0)
            total = quantity * unit_price
            self.total_var.set(f"{total:.2f}")
        except ValueError:
            pass

    def _validate_consumption_real_time(self, *args):
        """Validar consumo en tiempo real mientras el usuario escribe"""
        if not self.last_purchase_data:
            return

        try:
            consumed = float(self.consumed_var.get() or 0)
            remaining = float(self.remaining_var.get() or 0)

            if consumed == 0 and remaining == 0:
                self.validation_label.configure(text="", bootstyle="secondary")
                return

            # Obtener el total disponible
            last_quantity = self.last_purchase_data['quantity']
            initial_stock = self.last_purchase_data.get('initial_stock', 0.0)
            total_available = initial_stock + last_quantity

            # Calcular suma
            total_accounted = consumed + remaining
            difference = total_available - total_accounted

            # Mostrar mensaje según resultado
            if abs(difference) < 0.01:  # Tolerancia
                self.validation_label.configure(
                    text=f"✓ Perfecto: {consumed:.2f} + {remaining:.2f} = {total_available:.2f}",
                    bootstyle="success"
                )
            elif difference > 0:
                self.validation_label.configure(
                    text=f"⚠ Faltan {difference:.2f} por asignar (Total: {total_available:.2f})",
                    bootstyle="warning"
                )
            else:
                self.validation_label.configure(
                    text=f"✗ Te pasaste por {abs(difference):.2f} (Total: {total_available:.2f})",
                    bootstyle="danger"
                )

        except ValueError:
            self.validation_label.configure(text="", bootstyle="secondary")

    def save_purchase(self):
        """Save the purchase and consumption if applicable"""
        # Si está en modo edición, llamar a update_purchase
        if self.edit_mode:
            self.update_purchase()
            return

        # Validar datos de compra
        if not self.supply_id:
            Messagebox.show_error("Debe seleccionar un insumo", "Error")
            return

        # Validar proveedor
        supplier_name = self.supplier_var.get().strip()
        if not supplier_name:
            Messagebox.show_error("Debe seleccionar un proveedor", "Error")
            return

        supplier_id = self.suppliers_dict.get(supplier_name)
        if not supplier_id:
            Messagebox.show_error("Proveedor no válido", "Error")
            return

        unit = self.unit_var.get().strip()
        quantity = self.quantity_var.get().strip()
        unit_price = self.unit_price_var.get().strip()
        total_price = self.total_var.get().strip()
        notes = self.notes_text.get('1.0', 'end-1c').strip()

        if not unit or not quantity or not unit_price:
            Messagebox.show_error("Todos los campos marcados con * son obligatorios", "Error")
            return

        try:
            quantity = float(quantity)
            unit_price = float(unit_price)
            total_price = float(total_price) if total_price else quantity * unit_price
        except ValueError:
            Messagebox.show_error("Cantidad y precios deben ser números válidos", "Error")
            return

        # Obtener fecha del DateEntry
        try:
            # El DateEntry tiene un método para obtener la fecha directamente
            purchase_date = self.date_entry.entry.get()
            # Intentar parsear con el formato configurado: dd/mm/yyyy
            purchase_date = datetime.strptime(purchase_date, "%d/%m/%Y").date()
        except Exception as e:
            print(f"Error parsing date: {e}, using today")
            purchase_date = date.today()

        # Si no es la primera compra, validar y guardar consumo
        if not self.is_first_purchase:
            consumed = self.consumed_var.get().strip()
            remaining = self.remaining_var.get().strip()

            if not consumed or not remaining:
                Messagebox.show_error("Debe ingresar la cantidad consumida y restante", "Error")
                return

            try:
                consumed = float(consumed)
                remaining = float(remaining)
            except ValueError:
                Messagebox.show_error("Las cantidades deben ser números válidos", "Error")
                return

            # VALIDACIONES DE CONSUMO CON STOCK ACUMULATIVO
            if not self.last_purchase_data:
                Messagebox.show_error("Error: No se encontró información de la última compra", "Error")
                return

            last_quantity = self.last_purchase_data['quantity']
            last_unit = self.last_purchase_data['unit']
            initial_stock = self.last_purchase_data.get('initial_stock', 0.0)

            # Calcular el stock total disponible (stock anterior + última compra)
            total_available_stock = initial_stock + last_quantity

            # Validación 1: La cantidad consumida no puede ser mayor al stock total disponible
            if consumed > total_available_stock:
                Messagebox.show_error(
                    f"Error de validación:\n\n"
                    f"La cantidad consumida ({consumed:.2f} {last_unit}) no puede ser mayor "
                    f"al stock total disponible.\n\n"
                    f"Stock anterior: {initial_stock:.2f} {last_unit}\n"
                    f"Última compra: {last_quantity:.2f} {last_unit}\n"
                    f"Total disponible: {total_available_stock:.2f} {last_unit}\n\n"
                    f"Por favor, verifica los datos.",
                    "Error de Validación"
                )
                return

            # Validación 2: Consumido + Restante debe ser igual al stock total disponible
            total_accounted = consumed + remaining
            tolerance = 0.01  # Tolerancia para errores de redondeo

            if abs(total_accounted - total_available_stock) > tolerance:
                Messagebox.show_error(
                    f"Error de validación:\n\n"
                    f"La suma de consumido ({consumed:.2f} {last_unit}) + restante ({remaining:.2f} {last_unit}) "
                    f"= {total_accounted:.2f} {last_unit}\n\n"
                    f"No coincide con el stock total disponible: {total_available_stock:.2f} {last_unit}\n"
                    f"(Stock anterior: {initial_stock:.2f} + Compra: {last_quantity:.2f})\n\n"
                    f"Diferencia: {abs(total_accounted - total_available_stock):.2f} {last_unit}\n\n"
                    f"Por favor, verifica que los números sean correctos.",
                    "Error de Validación"
                )
                return

            # Validación 3: Las cantidades no pueden ser negativas
            if consumed < 0 or remaining < 0:
                Messagebox.show_error(
                    "Error de validación:\n\n"
                    "Las cantidades consumida y restante deben ser valores positivos.",
                    "Error de Validación"
                )
                return

            # Obtener fecha de última compra
            purchases = self.provider.get_purchases_by_supply(self.supply_id)
            last_purchase_date = purchases[0]['purchase_date']
            if isinstance(last_purchase_date, str):
                start_date = datetime.strptime(last_purchase_date, "%Y-%m-%d").date()
            elif isinstance(last_purchase_date, datetime):
                start_date = last_purchase_date.date()
            else:
                start_date = last_purchase_date

            consumption_notes = self.consumption_notes_text.get('1.0', 'end-1c').strip()

            # Guardar consumo
            success, result = self.provider.add_consumption(
                self.supply_id,
                start_date,
                purchase_date,
                consumed,
                remaining,
                unit,
                consumption_notes
            )

            if not success:
                Messagebox.show_error(f"Error al registrar el consumo: {result}", "Error")
                return

        # Guardar compra
        success, result = self.provider.add_purchase(
            self.supply_id,
            supplier_id,  # Ahora pasamos el supplier_id
            purchase_date,
            quantity,
            unit,
            unit_price,
            total_price,
            notes
        )

        if success:
            Messagebox.show_info("Compra registrada exitosamente", "Éxito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"Error al registrar la compra: {result}", "Error")

    def clear_form(self):
        """Clear the form"""
        self.supply_id = None
        self.supply_name = None
        self.suggested_supplier_id = None
        self.edit_mode = False
        self.purchase_id = None
        self.supply_label.configure(text="")
        self.supplier_var.set("")
        self.unit_var.set("")
        self.quantity_var.set("")
        self.unit_price_var.set("")
        self.total_var.set("")
        self.notes_text.delete('1.0', 'end')
        self.consumed_var.set("")
        self.remaining_var.set("")
        self.consumption_notes_text.delete('1.0', 'end')
        self.consumption_frame.pack_forget()
        # Restaurar título y botón para modo nuevo
        self.title_label.configure(text="Registrar Compra de Insumo")
        self.save_btn.configure(text="Guardar")

    def set_edit_mode(self, supply_id, supply_name, purchase_data):
        """Set the form in edit mode with existing purchase data"""
        self.edit_mode = True
        self.purchase_id = purchase_data.get('id')
        self.supply_id = supply_id
        self.supply_name = supply_name
        self.supply_label.configure(text=supply_name)
        self.last_purchase_data = None

        # Cambiar título y botón
        self.title_label.configure(text="Editar Compra de Insumo")
        self.save_btn.configure(text="Actualizar")

        # Cargar datos del proveedor
        supplier_name = purchase_data.get('supplier_name', '')
        if supplier_name:
            self.supplier_var.set(supplier_name)

        # Cargar fecha
        purchase_date = purchase_data.get('purchase_date')
        if purchase_date:
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            elif isinstance(purchase_date, datetime):
                purchase_date = purchase_date.date()
            self.date_entry.entry.delete(0, END)
            self.date_entry.entry.insert(0, purchase_date.strftime("%d/%m/%Y"))

        # Cargar unidad
        self.unit_var.set(purchase_data.get('unit', ''))

        # Cargar cantidad
        quantity = purchase_data.get('quantity', 0)
        self.quantity_var.set(f"{quantity:.2f}" if quantity else "")

        # Cargar precio unitario
        unit_price = purchase_data.get('unit_price', 0)
        self.unit_price_var.set(f"{unit_price:.2f}" if unit_price else "")

        # Cargar total
        total_price = purchase_data.get('total_price', 0)
        self.total_var.set(f"{total_price:.2f}" if total_price else "")

        # Cargar notas
        notes = purchase_data.get('notes', '')
        self.notes_text.delete('1.0', 'end')
        if notes:
            self.notes_text.insert('1.0', notes)

        # Buscar consumo asociado a esta compra y mostrarlo
        self._load_associated_consumption(supply_id, purchase_data)

    def _load_associated_consumption(self, supply_id, purchase_data):
        """Find and display the consumption associated with this purchase"""
        supply_full = self.provider.get_supply_by_id(supply_id)
        if not supply_full:
            self.consumption_frame.pack_forget()
            self.is_first_purchase = True
            return

        purchases = supply_full['purchases']
        consumptions = supply_full['consumptions']

        # Normalizar fecha de esta compra
        p_date = purchase_data['purchase_date']
        if isinstance(p_date, str):
            p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
        elif isinstance(p_date, datetime):
            p_date = p_date.date()

        # Encontrar la compra anterior (la que inició el período que terminó con esta compra)
        prev_purchase = None
        for i, p in enumerate(purchases):
            pd = p['purchase_date']
            if isinstance(pd, str):
                pd = datetime.strptime(pd, "%Y-%m-%d").date()
            elif isinstance(pd, datetime):
                pd = pd.date()

            if pd == p_date and i + 1 < len(purchases):
                prev_purchase = purchases[i + 1]
                break

        if not prev_purchase:
            # Es la primera compra, no hay consumo asociado
            self.consumption_frame.pack_forget()
            self.is_first_purchase = True
            return

        prev_date = prev_purchase['purchase_date']
        if isinstance(prev_date, str):
            prev_date = datetime.strptime(prev_date, "%Y-%m-%d").date()
        elif isinstance(prev_date, datetime):
            prev_date = prev_date.date()

        # Buscar consumo entre la compra anterior y esta compra
        associated_consumption = None
        for cons in consumptions:
            start = cons['start_date']
            if isinstance(start, str):
                start = datetime.strptime(start, "%Y-%m-%d").date()
            end = cons['end_date']
            if isinstance(end, str):
                end = datetime.strptime(end, "%Y-%m-%d").date()

            if start >= prev_date and end <= p_date:
                associated_consumption = cons
                break
            elif abs((start - prev_date).days) <= 2 and abs((end - p_date).days) <= 2:
                associated_consumption = cons
                break

        if not associated_consumption:
            self.consumption_frame.pack_forget()
            self.is_first_purchase = True
            return

        # Hay consumo asociado: mostrar la sección con los datos
        self.is_first_purchase = False
        self.last_purchase_data = prev_purchase

        # Llenar info de la compra anterior (la que inició el período)
        self.last_purchase_date_label.configure(text=prev_date.strftime("%d/%m/%Y"))
        self.last_purchase_quantity_label.configure(
            text=f"({prev_purchase['quantity']:.2f} {prev_purchase['unit']})"
        )

        # Stock anterior
        previous_stock = prev_purchase.get('initial_stock', 0.0)
        if previous_stock > 0:
            self.previous_stock_title_label.configure(text="Sobró de compra anterior:")
            self.previous_stock_label.configure(
                text=f"{previous_stock:.2f} {prev_purchase['unit']}"
            )
        else:
            self.previous_stock_title_label.configure(text="")
            self.previous_stock_label.configure(text="")

        # Total disponible
        total_available = previous_stock + prev_purchase['quantity']
        self.total_available_label.configure(
            text=f"{total_available:.2f} {prev_purchase['unit']}"
        )
        if previous_stock > 0:
            self.breakdown_label.configure(
                text=f"({previous_stock:.2f} sobrantes + {prev_purchase['quantity']:.2f} comprados)"
            )
        else:
            self.breakdown_label.configure(
                text=f"(Solo los {prev_purchase['quantity']:.2f} comprados)"
            )

        # Llenar campos de consumo con los valores existentes
        self.consumed_var.set(f"{associated_consumption['quantity_consumed']:.2f}")
        self.remaining_var.set(f"{associated_consumption['quantity_remaining']:.2f}")

        # Notas de consumo
        self.consumption_notes_text.delete('1.0', 'end')
        if associated_consumption.get('notes'):
            self.consumption_notes_text.insert('1.0', associated_consumption['notes'])

        # Mostrar la sección
        self.consumption_frame.pack(fill=X, pady=(10, 0))

    def update_purchase(self):
        """Update an existing purchase"""
        # Validar datos de compra
        if not self.supply_id or not self.purchase_id:
            Messagebox.show_error("Error: No se puede actualizar la compra", "Error")
            return

        # Validar proveedor
        supplier_name = self.supplier_var.get().strip()
        if not supplier_name:
            Messagebox.show_error("Debe seleccionar un proveedor", "Error")
            return

        supplier_id = self.suppliers_dict.get(supplier_name)
        if not supplier_id:
            Messagebox.show_error("Proveedor no válido", "Error")
            return

        unit = self.unit_var.get().strip()
        quantity = self.quantity_var.get().strip()
        unit_price = self.unit_price_var.get().strip()
        total_price = self.total_var.get().strip()
        notes = self.notes_text.get('1.0', 'end-1c').strip()

        if not unit or not quantity or not unit_price:
            Messagebox.show_error("Todos los campos marcados con * son obligatorios", "Error")
            return

        try:
            quantity = float(quantity)
            unit_price = float(unit_price)
            total_price = float(total_price) if total_price else quantity * unit_price
        except ValueError:
            Messagebox.show_error("Cantidad y precios deben ser números válidos", "Error")
            return

        # Obtener fecha del DateEntry
        try:
            purchase_date = self.date_entry.entry.get()
            purchase_date = datetime.strptime(purchase_date, "%d/%m/%Y").date()
        except Exception as e:
            print(f"Error parsing date: {e}, using today")
            purchase_date = date.today()

        # Actualizar compra
        success, result = self.provider.update_purchase(
            self.purchase_id,
            supplier_id,
            purchase_date,
            quantity,
            unit,
            unit_price,
            total_price,
            notes
        )

        if success:
            Messagebox.show_info("Compra actualizada exitosamente", "Éxito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"Error al actualizar la compra: {result}", "Error")
