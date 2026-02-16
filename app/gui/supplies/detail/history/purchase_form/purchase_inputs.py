import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.supplies import supply_provider


class PurchaseInputs(ttk.Frame):
    """Campos del formulario de compra: insumo, proveedor, fecha, unidad, cantidad, precio, notas"""

    def __init__(self, parent):
        super().__init__(parent)
        self.provider = supply_provider
        self.suppliers_dict = {}

        self.setup_ui()

    def setup_ui(self):
        # Insumo (readonly)
        ttk.Label(self, text="Insumo:*").pack(anchor=W, pady=(5, 2))
        self.supply_label = ttk.Label(self, text="", font=("Arial", 11, "bold"), bootstyle="info")
        self.supply_label.pack(anchor=W, pady=(0, 10))

        # Proveedor
        ttk.Label(self, text="Proveedor:*").pack(anchor=W, pady=(5, 2))
        self.supplier_var = ttk.StringVar()
        self.supplier_combo = ttk.Combobox(self, textvariable=self.supplier_var, values=[], width=28, state="readonly")
        self.supplier_combo.pack(fill=X, pady=(0, 10))
        self._load_suppliers()

        # Fecha de compra
        ttk.Label(self, text="Fecha de Compra:*").pack(anchor=W, pady=(5, 2))
        self.date_entry = ttk.DateEntry(self, bootstyle="primary", width=30, dateformat="%d/%m/%Y")
        self.date_entry.pack(fill=X, pady=(0, 10))
        self._patch_date_entry_position()

        # Unidad
        ttk.Label(self, text="Unidad:*").pack(anchor=W, pady=(5, 2))
        self.unit_var = ttk.StringVar()
        self.unit_combo = ttk.Combobox(
            self, textvariable=self.unit_var,
            values=["kilos", "litros", "piezas", "costales", "bultos", "cajas"], width=28
        )
        self.unit_combo.pack(fill=X, pady=(0, 10))

        # Cantidad
        ttk.Label(self, text="Cantidad:*").pack(anchor=W, pady=(5, 2))
        self.quantity_var = ttk.StringVar()
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_var, width=30)
        self.quantity_entry.pack(fill=X, pady=(0, 10))
        self.quantity_entry.bind('<KeyRelease>', self._calculate_total)

        # Precio unitario
        ttk.Label(self, text="Precio Unitario ($):*").pack(anchor=W, pady=(5, 2))
        self.unit_price_var = ttk.StringVar()
        self.unit_price_entry = ttk.Entry(self, textvariable=self.unit_price_var, width=30)
        self.unit_price_entry.pack(fill=X, pady=(0, 10))
        self.unit_price_entry.bind('<KeyRelease>', self._calculate_total)

        # Total
        ttk.Label(self, text="Total ($):").pack(anchor=W, pady=(5, 2))
        self.total_var = ttk.StringVar()
        self.total_entry = ttk.Entry(self, textvariable=self.total_var, width=30, state=READONLY)
        self.total_entry.pack(fill=X, pady=(0, 10))

        # Notas
        ttk.Label(self, text="Notas:").pack(anchor=W, pady=(5, 2))
        self.notes_text = ttk.Text(self, height=3, width=30)
        self.notes_text.pack(fill=X, pady=(0, 10))

    # ─── Helpers ──────────────────────────────────────────────────

    def _load_suppliers(self):
        suppliers = self.provider.get_suppliers_list()
        self.suppliers_dict = {name: id for id, name in suppliers}
        self.supplier_combo['values'] = list(self.suppliers_dict.keys())

    def _calculate_total(self, event=None):
        try:
            quantity = float(self.quantity_var.get() or 0)
            unit_price = float(self.unit_price_var.get() or 0)
            self.total_var.set(f"{quantity * unit_price:.2f}")
        except ValueError:
            pass

    def _patch_date_entry_position(self):
        """Override DateEntry calendar popup to not go off-screen"""
        original_on_date_ask = self.date_entry._on_date_ask

        def _on_date_ask_fixed():
            from ttkbootstrap.dialogs import DatePickerDialog
            original_set_pos = DatePickerDialog._set_window_position

            def _set_pos_left(dialog_self):
                if dialog_self.parent:
                    popup_width = dialog_self.root.winfo_reqwidth() or 226
                    screen_width = dialog_self.root.winfo_screenwidth()
                    entry_right = dialog_self.parent.winfo_rootx() + dialog_self.parent.winfo_width()
                    ypos = dialog_self.parent.winfo_rooty() + dialog_self.parent.winfo_height()
                    xpos = entry_right
                    if xpos + popup_width > screen_width:
                        xpos = entry_right - popup_width
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

    # ─── Clear ────────────────────────────────────────────────────

    def clear(self):
        self.supply_label.configure(text="")
        self.supplier_var.set("")
        self.unit_var.set("")
        self.quantity_var.set("")
        self.unit_price_var.set("")
        self.total_var.set("")
        self.notes_text.delete('1.0', 'end')
