import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ConsumptionInputs(ttk.Frame):
    """Campos del formulario de consumo del periodo"""

    def __init__(self, parent):
        super().__init__(parent)
        self.last_purchase_data = None

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(
            self, text="Registrar Consumo del Periodo",
            font=("Arial", 12, "bold"), bootstyle="warning"
        ).pack(anchor=W, pady=(5, 5))

        ttk.Label(
            self, text="¿Cuanto gastaste desde la ultima compra?",
            font=("Arial", 9, "italic"), bootstyle="secondary"
        ).pack(anchor=W, pady=(0, 10))

        # Info ultima compra
        ttk.Label(self, text="Ultima Compra:").pack(anchor=W, pady=(5, 2))

        last_info = ttk.Frame(self)
        last_info.pack(fill=X, pady=(0, 10))

        self.last_purchase_date_label = ttk.Label(last_info, text="", font=("Arial", 10, "bold"))
        self.last_purchase_date_label.pack(side=LEFT)

        self.last_purchase_quantity_label = ttk.Label(last_info, text="", font=("Arial", 10, "bold"), bootstyle="info")
        self.last_purchase_quantity_label.pack(side=LEFT, padx=(10, 0))

        # Stock anterior
        self.previous_stock_title_label = ttk.Label(self, text="", font=("Arial", 10))
        self.previous_stock_title_label.pack(anchor=W, pady=(5, 2))

        self.previous_stock_label = ttk.Label(self, text="", font=("Arial", 10, "bold"), bootstyle="secondary")
        self.previous_stock_label.pack(anchor=W, pady=(0, 5))

        # Total disponible
        self.total_available_frame = ttk.Labelframe(
            self, text="  Total Disponible en el Periodo  ",
            bootstyle="info", padding=10
        )
        self.total_available_frame.pack(fill=X, pady=(5, 15))

        self.total_available_label = ttk.Label(self.total_available_frame, text="", font=("Arial", 14, "bold"), bootstyle="info")
        self.total_available_label.pack()

        self.breakdown_label = ttk.Label(self.total_available_frame, text="", font=("Arial", 8, "italic"), bootstyle="secondary")
        self.breakdown_label.pack(pady=(2, 0))

        # Cantidad consumida
        consumed_lf = ttk.Frame(self)
        consumed_lf.pack(fill=X, pady=(5, 2))
        ttk.Label(consumed_lf, text="¿Cuanto Gastaste?*", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(consumed_lf, text="(puede incluir lo sobrante)", font=("Arial", 8, "italic"), bootstyle="secondary").pack(side=LEFT, padx=(5, 0))

        self.consumed_var = ttk.StringVar()
        self.consumed_entry = ttk.Entry(self, textvariable=self.consumed_var, width=30, font=("Arial", 11))
        self.consumed_entry.pack(fill=X, pady=(0, 10))

        # Cantidad restante
        remaining_lf = ttk.Frame(self)
        remaining_lf.pack(fill=X, pady=(5, 2))
        ttk.Label(remaining_lf, text="¿Cuanto Sobro?*", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(remaining_lf, text="(lo que no usaste)", font=("Arial", 8, "italic"), bootstyle="secondary").pack(side=LEFT, padx=(5, 0))

        self.remaining_var = ttk.StringVar()
        self.remaining_entry = ttk.Entry(self, textvariable=self.remaining_var, width=30, font=("Arial", 11))
        self.remaining_entry.pack(fill=X, pady=(0, 5))

        # Validacion en tiempo real
        self.validation_label = ttk.Label(self, text="", font=("Arial", 9), bootstyle="secondary")
        self.validation_label.pack(anchor=W, pady=(0, 10))

        self.consumed_var.trace_add('write', self._validate_real_time)
        self.remaining_var.trace_add('write', self._validate_real_time)

        # Notas de consumo
        ttk.Label(self, text="Notas de Consumo:").pack(anchor=W, pady=(5, 2))
        self.consumption_notes_text = ttk.Text(self, height=2, width=30)
        self.consumption_notes_text.pack(fill=X, pady=(0, 10))

    # ─── Validacion ───────────────────────────────────────────────

    def _validate_real_time(self, *args):
        if not self.last_purchase_data:
            return
        try:
            consumed = float(self.consumed_var.get() or 0)
            remaining = float(self.remaining_var.get() or 0)

            if consumed == 0 and remaining == 0:
                self.validation_label.configure(text="", bootstyle="secondary")
                return

            last_quantity = self.last_purchase_data['quantity']
            initial_stock = self.last_purchase_data.get('initial_stock', 0.0)
            total_available = initial_stock + last_quantity
            total_accounted = consumed + remaining
            difference = total_available - total_accounted

            if abs(difference) < 0.01:
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

    # ─── Clear ────────────────────────────────────────────────────

    def clear(self):
        self.last_purchase_data = None
        self.consumed_var.set("")
        self.remaining_var.set("")
        self.consumption_notes_text.delete('1.0', 'end')
        self.validation_label.configure(text="", bootstyle="secondary")
