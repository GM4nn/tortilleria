import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, date
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

        self.setup_ui()

    def setup_ui(self):
        """Setup the form UI"""
        # Header with title and close button
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 20), padx=20)

        ttk.Label(
            header_frame,
            text="Registrar Compra de Insumo",
            font=("Arial", 16, "bold")
        ).pack(side=LEFT)

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

        # Separador
        ttk.Separator(self.consumption_frame, orient=HORIZONTAL).pack(fill=X, pady=10)

        ttk.Label(
            self.consumption_frame,
            text="¿Cuánto consumiste desde la última compra?",
            font=("Arial", 12, "bold"),
            bootstyle="warning"
        ).pack(anchor=W, pady=(5, 10))

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

        # Cantidad consumida
        ttk.Label(self.consumption_frame, text="Cantidad Consumida:*").pack(anchor=W, pady=(5, 2))
        self.consumed_var = ttk.StringVar()
        self.consumed_entry = ttk.Entry(
            self.consumption_frame,
            textvariable=self.consumed_var,
            width=30
        )
        self.consumed_entry.pack(fill=X, pady=(0, 10))

        # Cantidad restante
        ttk.Label(self.consumption_frame, text="Cantidad Restante:*").pack(anchor=W, pady=(5, 2))
        self.remaining_var = ttk.StringVar()
        self.remaining_entry = ttk.Entry(
            self.consumption_frame,
            textvariable=self.remaining_var,
            width=30
        )
        self.remaining_entry.pack(fill=X, pady=(0, 10))

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

        ttk.Button(
            btn_frame,
            text="Guardar",
            command=self.save_purchase,
            bootstyle="success",
            width=15
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.on_close_callback,
            bootstyle="secondary",
            width=15
        ).pack(side=LEFT)

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

                self.consumption_frame.pack(fill=X, pady=(10, 0))
        else:
            self.consumption_frame.pack_forget()

        # Establecer fecha de hoy por defecto (formato dd/mm/yyyy)
        self.date_entry.entry.delete(0, END)
        self.date_entry.entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

    def calculate_total(self, event=None):
        """Calculate total price"""
        try:
            quantity = float(self.quantity_var.get() or 0)
            unit_price = float(self.unit_price_var.get() or 0)
            total = quantity * unit_price
            self.total_var.set(f"{total:.2f}")
        except ValueError:
            pass

    def save_purchase(self):
        """Save the purchase and consumption if applicable"""
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

            # VALIDACIONES DE CONSUMO
            if not self.last_purchase_data:
                Messagebox.show_error("Error: No se encontró información de la última compra", "Error")
                return

            last_quantity = self.last_purchase_data['quantity']
            last_unit = self.last_purchase_data['unit']

            # Validación 1: La cantidad consumida no puede ser mayor a la comprada
            if consumed > last_quantity:
                Messagebox.show_error(
                    f"Error de validación:\n\n"
                    f"La cantidad consumida ({consumed:.2f} {last_unit}) no puede ser mayor "
                    f"a la cantidad comprada en la última compra ({last_quantity:.2f} {last_unit}).\n\n"
                    f"Por favor, verifica los datos.",
                    "Error de Validación"
                )
                return

            # Validación 2: Consumido + Restante debe ser igual a la cantidad comprada
            total_accounted = consumed + remaining
            tolerance = 0.01  # Tolerancia para errores de redondeo

            if abs(total_accounted - last_quantity) > tolerance:
                Messagebox.show_error(
                    f"Error de validación:\n\n"
                    f"La suma de consumido ({consumed:.2f} {last_unit}) + restante ({remaining:.2f} {last_unit}) "
                    f"= {total_accounted:.2f} {last_unit}\n\n"
                    f"No coincide con la cantidad comprada: {last_quantity:.2f} {last_unit}\n\n"
                    f"Diferencia: {abs(total_accounted - last_quantity):.2f} {last_unit}\n\n"
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
