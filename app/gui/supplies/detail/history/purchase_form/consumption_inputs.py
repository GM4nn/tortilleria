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
            self, text="Consumo del Periodo Anterior",
            font=("Arial", 12, "bold"), bootstyle="warning"
        ).pack(anchor=W, pady=(5, 5))

        ttk.Label(
            self, text="Ingresa cuanto te sobro del periodo anterior",
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

        # Cantidad restante (input del usuario)
        ttk.Label(self, text="¿Cuanto Sobro?*", font=("Arial", 10, "bold")).pack(anchor=W, pady=(5, 2))

        self.remaining_var = ttk.StringVar()
        self.remaining_entry = ttk.Entry(self, textvariable=self.remaining_var, width=30, font=("Arial", 11))
        self.remaining_entry.pack(fill=X, pady=(0, 10))

        # Consumido (auto-calculado, solo informativo)
        self.consumed_label = ttk.Label(self, text="", font=("Arial", 10), bootstyle="secondary")
        self.consumed_label.pack(anchor=W, pady=(0, 5))

        # Validacion en tiempo real
        self.validation_label = ttk.Label(self, text="", font=("Arial", 9), bootstyle="secondary")
        self.validation_label.pack(anchor=W, pady=(0, 10))

        self.remaining_var.trace_add('write', self._validate_real_time)

    # ─── Validacion ───────────────────────────────────────────────

    def _validate_real_time(self, *args):
        if not self.last_purchase_data:
            return
        try:
            user_remaining = float(self.remaining_var.get() or 0)

            last_quantity = self.last_purchase_data['quantity']
            prev_remaining = self.last_purchase_data.get('remaining', 0.0)
            total_available = prev_remaining + last_quantity
            consumed = total_available - user_remaining

            if user_remaining < 0:
                self.consumed_label.configure(text="")
                self.validation_label.configure(text="El restante no puede ser negativo", bootstyle="danger")
            elif user_remaining > total_available:
                self.consumed_label.configure(text="")
                self.validation_label.configure(
                    text=f"No puede sobrar mas de lo disponible ({total_available:.2f})",
                    bootstyle="danger"
                )
            else:
                self.consumed_label.configure(
                    text=f"Consumido: {consumed:.2f} ({consumed / total_available * 100:.0f}%)" if total_available > 0 else "",
                    bootstyle="info"
                )
                self.validation_label.configure(
                    text=f"Gastaste {consumed:.2f} + Sobro {user_remaining:.2f} = {total_available:.2f}",
                    bootstyle="success"
                )
        except ValueError:
            self.consumed_label.configure(text="")
            self.validation_label.configure(text="", bootstyle="secondary")

    # ─── Clear ────────────────────────────────────────────────────

    def clear(self):
        self.last_purchase_data = None
        self.remaining_var.set("")
        self.consumed_label.configure(text="")
        self.validation_label.configure(text="", bootstyle="secondary")
