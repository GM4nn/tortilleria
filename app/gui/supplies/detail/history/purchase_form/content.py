import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, date
from app.constants import mexico_now
from app.data.providers.supplies import supply_provider
from app.gui.supplies.detail.history.purchase_form.purchase_inputs import PurchaseInputs
from app.gui.supplies.detail.history.purchase_form.consumption_inputs import ConsumptionInputs


class PurchaseForm(ttk.Frame):
    """Coordinador del formulario de compras: header + purchase inputs + consumption inputs + action buttons"""

    def __init__(self, parent, app, on_close_callback):
        super().__init__(parent)
        self.app = app
        self.provider = supply_provider
        self.on_close_callback = on_close_callback
        self.supply_id = None
        self.supply_name = None
        self.suggested_supplier_id = None
        self.is_first_purchase = True
        self.edit_mode = False
        self.purchase_id = None
        self.last_purchase_data = None

        self.setup_ui()

    # ─── UI Setup ─────────────────────────────────────────────────

    def setup_ui(self):
        self._setup_header()

        # Canvas scrollable
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=BOTH, expand=YES, padx=20)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.form_container = ttk.Frame(self.canvas)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.form_container, anchor="nw")
        self.form_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Componentes del formulario
        self.purchase_inputs = PurchaseInputs(self.form_container)
        self.purchase_inputs.pack(fill=X)

        self.consumption_inputs = ConsumptionInputs(self.form_container)
        # No se empaca hasta que se necesite (pack_forget por defecto)

        self._setup_action_buttons()

    def _setup_header(self):
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

    def _setup_action_buttons(self):
        """Botones de accion fijos al fondo"""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=(10, 0), padx=20, side=BOTTOM)

        ttk.Button(
            btn_frame, text="Nuevo", command=self._new_purchase,
            bootstyle="success", width=20
        ).pack(fill=X, pady=5)

        self.save_btn = ttk.Button(
            btn_frame, text="Guardar", command=self.save_purchase,
            bootstyle="primary", width=20
        )
        self.save_btn.pack(fill=X, pady=5)

        self.delete_btn = ttk.Button(
            btn_frame, text="Eliminar", command=self._delete_purchase,
            bootstyle="danger", width=20
        )
        self.delete_btn.pack(fill=X, pady=5)
        self.delete_btn.configure(state=DISABLED)

        ttk.Button(
            btn_frame, text="Limpiar", command=self._on_clear,
            bootstyle="secondary-outline", width=20
        ).pack(fill=X, pady=5)

    def _new_purchase(self):
        sid, sname, sup_id, unit = self.supply_id, self.supply_name, self.suggested_supplier_id, getattr(self, 'supply_unit', None)
        self.clear_form()
        if sid and sname:
            self.set_supply(sid, sname, sup_id, unit)
        self.purchase_inputs.date_entry.entry.focus()

    def _delete_purchase(self):
        if not self.edit_mode or not self.purchase_id:
            return

        confirm = Messagebox.yesno(
            "¿Esta seguro que desea eliminar esta compra?",
            "Confirmar eliminacion"
        )
        if confirm != "Yes":
            return

        success, result = self.provider.delete_purchase(self.purchase_id)
        if success:
            Messagebox.show_info("Compra eliminada exitosamente", "Exito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"Error al eliminar: {result}", "Error")

    def _on_clear(self):
        sid, sname, sup_id, unit = self.supply_id, self.supply_name, self.suggested_supplier_id, getattr(self, 'supply_unit', None)
        self.clear_form()
        if sid and sname:
            self.set_supply(sid, sname, sup_id, unit)

    # ─── Set supply / Edit mode ───────────────────────────────────

    def set_supply(self, supply_id, supply_name, suggested_supplier_id=None, unit=None):
        self.supply_id = supply_id
        self.supply_name = supply_name
        self.suggested_supplier_id = suggested_supplier_id
        self.supply_unit = unit
        self.purchase_inputs.supply_label.configure(text=supply_name)
        if unit:
            self.purchase_inputs.unit_var.set(unit)
        self.last_purchase_data = None

        if suggested_supplier_id:
            for name, sid in self.purchase_inputs.suppliers_dict.items():
                if sid == suggested_supplier_id:
                    self.purchase_inputs.supplier_var.set(name)
                    break

        self.is_first_purchase = not self.provider.has_previous_purchases(supply_id)

        if not self.is_first_purchase:
            purchases = self.provider.get_purchases_by_supply(supply_id)
            if purchases:
                last_purchase = purchases[0]
                self.last_purchase_data = last_purchase
                self.consumption_inputs.last_purchase_data = last_purchase
                self._fill_consumption_info(last_purchase, supply_id)
                self.consumption_inputs.pack(fill=X, pady=(10, 0))
        else:
            self.consumption_inputs.pack_forget()

        self.purchase_inputs.date_entry.entry.delete(0, END)
        self.purchase_inputs.date_entry.entry.insert(0, mexico_now().strftime("%d/%m/%Y"))

    def _fill_consumption_info(self, last_purchase, supply_id):
        """Llenar los labels de info de consumo con datos de la ultima compra"""
        last_date = last_purchase['purchase_date']
        if isinstance(last_date, str):
            last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
        elif isinstance(last_date, datetime):
            last_date = last_date.date()

        ci = self.consumption_inputs
        ci.last_purchase_date_label.configure(text=last_date.strftime("%d/%m/%Y"))
        ci.last_purchase_quantity_label.configure(text=f"({last_purchase['quantity']:.2f} {last_purchase['unit']})")

        previous_stock = last_purchase.get('remaining', 0.0)

        if previous_stock > 0:
            ci.previous_stock_label.configure(text=f"{previous_stock:.2f} {last_purchase['unit']}")
            purchases = self.provider.get_purchases_by_supply(supply_id)
            if len(purchases) >= 2:
                prev_prev_date = purchases[1]['purchase_date']
                if isinstance(prev_prev_date, str):
                    prev_prev_date = datetime.strptime(prev_prev_date, "%Y-%m-%d").date()
                elif isinstance(prev_prev_date, datetime):
                    prev_prev_date = prev_prev_date.date()
                ci.previous_stock_title_label.configure(text=f"Sobro de {prev_prev_date.strftime('%d/%m/%Y')}:")
            else:
                ci.previous_stock_title_label.configure(text="Sobro de compra anterior:")
        else:
            ci.previous_stock_title_label.configure(text="")
            ci.previous_stock_label.configure(text="")

        total_available = previous_stock + last_purchase['quantity']
        ci.total_available_label.configure(text=f"{total_available:.2f} {last_purchase['unit']}")

        if previous_stock > 0:
            ci.breakdown_label.configure(text=f"({previous_stock:.2f} sobrantes + {last_purchase['quantity']:.2f} comprados)")
        else:
            ci.breakdown_label.configure(text=f"(Solo los {last_purchase['quantity']:.2f} comprados)")

    def set_edit_mode(self, supply_id, supply_name, purchase_data):
        self.edit_mode = True
        self.purchase_id = purchase_data.get('id')
        self.supply_id = supply_id
        self.supply_name = supply_name
        self.purchase_inputs.supply_label.configure(text=supply_name)
        self.last_purchase_data = None

        self.title_label.configure(text="Editar Compra de Insumo")
        self.save_btn.configure(text="Actualizar")
        self.delete_btn.configure(state=NORMAL)

        pi = self.purchase_inputs

        supplier_name = purchase_data.get('supplier_name', '')
        if supplier_name:
            pi.supplier_var.set(supplier_name)

        purchase_date = purchase_data.get('purchase_date')
        if purchase_date:
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            elif isinstance(purchase_date, datetime):
                purchase_date = purchase_date.date()
            pi.date_entry.entry.delete(0, END)
            pi.date_entry.entry.insert(0, purchase_date.strftime("%d/%m/%Y"))

        pi.unit_var.set(purchase_data.get('unit', ''))

        quantity = purchase_data.get('quantity', 0)
        pi.quantity_var.set(f"{quantity:.2f}" if quantity else "")

        unit_price = purchase_data.get('unit_price', 0)
        pi.unit_price_var.set(f"{unit_price:.2f}" if unit_price else "")

        total_price = purchase_data.get('total_price', 0)
        pi.total_var.set(f"{total_price:.2f}" if total_price else "")

        notes = purchase_data.get('notes', '')
        pi.notes_text.delete('1.0', 'end')
        if notes:
            pi.notes_text.insert('1.0', notes)

        self._load_associated_consumption(supply_id, purchase_data)

    # ─── Associated consumption ───────────────────────────────────

    def _load_associated_consumption(self, supply_id, purchase_data):
        """Cargar consumo asociado buscando la compra previa"""
        purchases = self.provider.get_purchases_by_supply(supply_id)
        if not purchases:
            self.consumption_inputs.pack_forget()
            self.is_first_purchase = True
            return

        p_date = purchase_data['purchase_date']
        if isinstance(p_date, str):
            p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
        elif isinstance(p_date, datetime):
            p_date = p_date.date()

        # Buscar la compra previa a la que estamos editando
        prev_purchase = None
        prev_prev_purchase = None
        for i, p in enumerate(purchases):
            pd = p['purchase_date']
            if isinstance(pd, str):
                pd = datetime.strptime(pd, "%Y-%m-%d").date()
            elif isinstance(pd, datetime):
                pd = pd.date()
            if pd == p_date and i + 1 < len(purchases):
                prev_purchase = purchases[i + 1]
                if i + 2 < len(purchases):
                    prev_prev_purchase = purchases[i + 2]
                break

        if not prev_purchase:
            self.consumption_inputs.pack_forget()
            self.is_first_purchase = True
            return

        prev_date = prev_purchase['purchase_date']
        if isinstance(prev_date, str):
            prev_date = datetime.strptime(prev_date, "%Y-%m-%d").date()
        elif isinstance(prev_date, datetime):
            prev_date = prev_date.date()

        self.is_first_purchase = False
        self.last_purchase_data = prev_purchase
        self.consumption_inputs.last_purchase_data = prev_purchase

        ci = self.consumption_inputs

        ci.last_purchase_date_label.configure(text=prev_date.strftime("%d/%m/%Y"))
        ci.last_purchase_quantity_label.configure(text=f"({prev_purchase['quantity']:.2f} {prev_purchase['unit']})")

        previous_stock = prev_purchase.get('remaining', 0.0)
        if previous_stock > 0:
            if prev_prev_purchase:
                pp_date = prev_prev_purchase['purchase_date']
                if isinstance(pp_date, str):
                    pp_date = datetime.strptime(pp_date, "%Y-%m-%d").date()
                elif isinstance(pp_date, datetime):
                    pp_date = pp_date.date()
                ci.previous_stock_title_label.configure(text=f"Sobro de compra anterior ({pp_date.strftime('%d/%m/%Y')}):")
            else:
                ci.previous_stock_title_label.configure(text="Sobro de compra anterior:")
            ci.previous_stock_label.configure(text=f"{previous_stock:.2f} {prev_purchase['unit']}")
        else:
            ci.previous_stock_title_label.configure(text="")
            ci.previous_stock_label.configure(text="")

        total_available = previous_stock + prev_purchase['quantity']
        ci.total_available_label.configure(text=f"{total_available:.2f} {prev_purchase['unit']}")
        if previous_stock > 0:
            ci.breakdown_label.configure(text=f"({previous_stock:.2f} sobrantes + {prev_purchase['quantity']:.2f} comprados)")
        else:
            ci.breakdown_label.configure(text=f"(Solo los {prev_purchase['quantity']:.2f} comprados)")

        # Cargar remaining del purchase actual (en modo edicion)
        current_remaining = purchase_data.get('remaining', 0.0)
        ci.remaining_var.set(f"{current_remaining:.2f}")

        ci.pack(fill=X, pady=(10, 0))

    # ─── Save / Update ────────────────────────────────────────────

    def save_purchase(self):
        if self.edit_mode:
            self._update_purchase()
            return

        if not self.supply_id:
            Messagebox.show_error("Debe seleccionar un insumo", "Error")
            return

        pi = self.purchase_inputs

        supplier_name = pi.supplier_var.get().strip()
        if not supplier_name:
            Messagebox.show_error("Debe seleccionar un proveedor", "Error")
            return

        supplier_id = pi.suppliers_dict.get(supplier_name)
        if not supplier_id:
            Messagebox.show_error("Proveedor no valido", "Error")
            return

        unit = pi.unit_var.get().strip()
        quantity = pi.quantity_var.get().strip()
        unit_price = pi.unit_price_var.get().strip()
        total_price = pi.total_var.get().strip()
        notes = pi.notes_text.get('1.0', 'end-1c').strip()

        if not unit or not quantity or not unit_price:
            Messagebox.show_error("Todos los campos marcados con * son obligatorios", "Error")
            return

        try:
            quantity = float(quantity)
            unit_price = float(unit_price)
            total_price = float(total_price) if total_price else quantity * unit_price
        except ValueError:
            Messagebox.show_error("Cantidad y precios deben ser numeros validos", "Error")
            return

        try:
            purchase_date = datetime.strptime(pi.date_entry.entry.get(), "%d/%m/%Y").date()
        except Exception:
            purchase_date = date.today()

        # Obtener remaining (lo que sobro del periodo anterior)
        remaining = 0.0
        if not self.is_first_purchase:
            remaining = self._validate_consumption()
            if remaining is None:
                return  # Validacion fallo

        success, result = self.provider.add_purchase(
            self.supply_id, supplier_id, purchase_date,
            quantity, unit, unit_price, total_price, remaining, notes
        )

        if success:
            Messagebox.show_info("Compra registrada exitosamente", "Exito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"Error al registrar la compra: {result}", "Error")

    def _validate_consumption(self):
        """Validar remaining. Retorna remaining si OK, None si error."""
        ci = self.consumption_inputs
        remaining_str = ci.remaining_var.get().strip()

        if not remaining_str:
            Messagebox.show_error("Debe ingresar la cantidad restante", "Error")
            return None

        try:
            remaining = float(remaining_str)
        except ValueError:
            Messagebox.show_error("La cantidad debe ser un numero valido", "Error")
            return None

        if remaining < 0:
            Messagebox.show_error("La cantidad restante no puede ser negativa", "Error de Validacion")
            return None

        if not self.last_purchase_data:
            Messagebox.show_error("Error: No se encontro informacion de la ultima compra", "Error")
            return None

        last_quantity = self.last_purchase_data['quantity']
        prev_remaining = self.last_purchase_data.get('remaining', 0.0)
        total_available = prev_remaining + last_quantity

        if remaining > total_available:
            Messagebox.show_error(
                f"No puede sobrar mas ({remaining:.2f}) de lo que habia disponible ({total_available:.2f})",
                "Error de Validacion"
            )
            return None

        return remaining

    def _update_purchase(self):
        if not self.supply_id or not self.purchase_id:
            Messagebox.show_error("Error: No se puede actualizar la compra", "Error")
            return

        pi = self.purchase_inputs

        supplier_name = pi.supplier_var.get().strip()
        if not supplier_name:
            Messagebox.show_error("Debe seleccionar un proveedor", "Error")
            return

        supplier_id = pi.suppliers_dict.get(supplier_name)
        if not supplier_id:
            Messagebox.show_error("Proveedor no valido", "Error")
            return

        unit = pi.unit_var.get().strip()
        quantity = pi.quantity_var.get().strip()
        unit_price = pi.unit_price_var.get().strip()
        total_price = pi.total_var.get().strip()
        notes = pi.notes_text.get('1.0', 'end-1c').strip()

        if not unit or not quantity or not unit_price:
            Messagebox.show_error("Todos los campos marcados con * son obligatorios", "Error")
            return

        try:
            quantity = float(quantity)
            unit_price = float(unit_price)
            total_price = float(total_price) if total_price else quantity * unit_price
        except ValueError:
            Messagebox.show_error("Cantidad y precios deben ser numeros validos", "Error")
            return

        try:
            purchase_date = datetime.strptime(pi.date_entry.entry.get(), "%d/%m/%Y").date()
        except Exception:
            purchase_date = date.today()

        # Obtener remaining si no es primera compra
        remaining = None
        if not self.is_first_purchase:
            remaining = self._validate_consumption()
            if remaining is None:
                return

        success, result = self.provider.update_purchase(
            self.purchase_id, supplier_id, purchase_date,
            quantity, unit, unit_price, total_price, remaining, notes
        )

        if success:
            Messagebox.show_info("Compra actualizada exitosamente", "Exito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"Error al actualizar la compra: {result}", "Error")

    # ─── Clear ────────────────────────────────────────────────────

    def clear_form(self):
        self.supply_id = None
        self.supply_name = None
        self.suggested_supplier_id = None
        self.edit_mode = False
        self.purchase_id = None
        self.last_purchase_data = None

        self.purchase_inputs.clear()
        self.consumption_inputs.clear()
        self.consumption_inputs.pack_forget()

        self.title_label.configure(text="Registrar Compra de Insumo")
        self.save_btn.configure(text="Guardar")
        self.delete_btn.configure(state=DISABLED)
