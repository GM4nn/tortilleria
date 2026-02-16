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

        self.save_btn = ttk.Button(btn_frame, text="Guardar", command=self.save_purchase, bootstyle="success", width=15)
        self.save_btn.pack(side=LEFT, padx=(0, 10))

        ttk.Button(btn_frame, text="Cancelar", command=self.on_close_callback, bootstyle="secondary", width=15).pack(side=LEFT)

    # ─── Set supply / Edit mode ───────────────────────────────────

    def set_supply(self, supply_id, supply_name, suggested_supplier_id=None):
        self.supply_id = supply_id
        self.supply_name = supply_name
        self.suggested_supplier_id = suggested_supplier_id
        self.purchase_inputs.supply_label.configure(text=supply_name)
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

        previous_stock = last_purchase.get('initial_stock', 0.0)

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
        supply_full = self.provider.get_supply_by_id(supply_id)
        if not supply_full:
            self.consumption_inputs.pack_forget()
            self.is_first_purchase = True
            return

        purchases = supply_full['purchases']
        consumptions = supply_full['consumptions']

        p_date = purchase_data['purchase_date']
        if isinstance(p_date, str):
            p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
        elif isinstance(p_date, datetime):
            p_date = p_date.date()

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
            self.consumption_inputs.pack_forget()
            self.is_first_purchase = True
            return

        prev_date = prev_purchase['purchase_date']
        if isinstance(prev_date, str):
            prev_date = datetime.strptime(prev_date, "%Y-%m-%d").date()
        elif isinstance(prev_date, datetime):
            prev_date = prev_date.date()

        associated = None
        for cons in consumptions:
            start = cons['start_date']
            if isinstance(start, str):
                start = datetime.strptime(start, "%Y-%m-%d").date()
            end = cons['end_date']
            if isinstance(end, str):
                end = datetime.strptime(end, "%Y-%m-%d").date()

            if start >= prev_date and end <= p_date:
                associated = cons
                break
            elif abs((start - prev_date).days) <= 2 and abs((end - p_date).days) <= 2:
                associated = cons
                break

        if not associated:
            self.consumption_inputs.pack_forget()
            self.is_first_purchase = True
            return

        self.is_first_purchase = False
        self.last_purchase_data = prev_purchase
        self.consumption_inputs.last_purchase_data = prev_purchase

        ci = self.consumption_inputs

        ci.last_purchase_date_label.configure(text=prev_date.strftime("%d/%m/%Y"))
        ci.last_purchase_quantity_label.configure(text=f"({prev_purchase['quantity']:.2f} {prev_purchase['unit']})")

        previous_stock = prev_purchase.get('initial_stock', 0.0)
        if previous_stock > 0:
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

        ci.consumed_var.set(f"{associated['quantity_consumed']:.2f}")
        ci.remaining_var.set(f"{associated['quantity_remaining']:.2f}")

        ci.consumption_notes_text.delete('1.0', 'end')
        if associated.get('notes'):
            ci.consumption_notes_text.insert('1.0', associated['notes'])

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

        if not self.is_first_purchase:
            if not self._validate_and_save_consumption(unit, purchase_date):
                return

        success, result = self.provider.add_purchase(
            self.supply_id, supplier_id, purchase_date,
            quantity, unit, unit_price, total_price, notes
        )

        if success:
            Messagebox.show_info("Compra registrada exitosamente", "Exito")
            self.clear_form()
            if self.on_close_callback:
                self.on_close_callback()
        else:
            Messagebox.show_error(f"Error al registrar la compra: {result}", "Error")

    def _validate_and_save_consumption(self, unit, purchase_date):
        """Validar consumo y guardarlo. Retorna True si OK, False si error."""
        ci = self.consumption_inputs

        consumed = ci.consumed_var.get().strip()
        remaining = ci.remaining_var.get().strip()

        if not consumed or not remaining:
            Messagebox.show_error("Debe ingresar la cantidad consumida y restante", "Error")
            return False

        try:
            consumed = float(consumed)
            remaining = float(remaining)
        except ValueError:
            Messagebox.show_error("Las cantidades deben ser numeros validos", "Error")
            return False

        if not self.last_purchase_data:
            Messagebox.show_error("Error: No se encontro informacion de la ultima compra", "Error")
            return False

        last_quantity = self.last_purchase_data['quantity']
        last_unit = self.last_purchase_data['unit']
        initial_stock = self.last_purchase_data.get('initial_stock', 0.0)
        total_available_stock = initial_stock + last_quantity

        if consumed > total_available_stock:
            Messagebox.show_error(
                f"La cantidad consumida ({consumed:.2f} {last_unit}) no puede ser mayor "
                f"al stock total disponible ({total_available_stock:.2f} {last_unit}).",
                "Error de Validacion"
            )
            return False

        total_accounted = consumed + remaining
        if abs(total_accounted - total_available_stock) > 0.01:
            Messagebox.show_error(
                f"Consumido ({consumed:.2f}) + Restante ({remaining:.2f}) = {total_accounted:.2f}\n"
                f"No coincide con el total disponible: {total_available_stock:.2f}",
                "Error de Validacion"
            )
            return False

        if consumed < 0 or remaining < 0:
            Messagebox.show_error("Las cantidades deben ser valores positivos.", "Error de Validacion")
            return False

        purchases = self.provider.get_purchases_by_supply(self.supply_id)
        last_purchase_date = purchases[0]['purchase_date']
        if isinstance(last_purchase_date, str):
            start_date = datetime.strptime(last_purchase_date, "%Y-%m-%d").date()
        elif isinstance(last_purchase_date, datetime):
            start_date = last_purchase_date.date()
        else:
            start_date = last_purchase_date

        consumption_notes = ci.consumption_notes_text.get('1.0', 'end-1c').strip()

        success, result = self.provider.add_consumption(
            self.supply_id, start_date, purchase_date,
            consumed, remaining, unit, consumption_notes
        )

        if not success:
            Messagebox.show_error(f"Error al registrar el consumo: {result}", "Error")
            return False

        return True

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

        success, result = self.provider.update_purchase(
            self.purchase_id, supplier_id, purchase_date,
            quantity, unit, unit_price, total_price, notes
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
