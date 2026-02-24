import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *


class PaymentDialog(ttk.Toplevel):
    """Dialogo modal para registrar el pago restante al completar un pedido."""

    def __init__(self, parent, order_data):
        super().__init__(parent)
        self.order_data = order_data
        self.result = None  # None = cancelado, float = monto del pago final

        self.total = order_data['total']
        self.already_paid = order_data.get('amount_paid', 0.0) or 0.0
        self.remaining = round(self.total - self.already_paid, 2)

        self.title(f"Pago Pendiente - Pedido #{order_data['id']}")
        self.geometry("420x360")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.center_on_parent(parent)

    def setup_ui(self):
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text=f"Pedido #{self.order_data['id']}",
            font=("Arial", 14, "bold")
        ).pack(anchor=W)

        ttk.Label(
            header,
            text="Este pedido tiene un saldo pendiente.\nIngrese el monto del pago para completar.",
            font=("Arial", 9),
            bootstyle="secondary",
            wraplength=380
        ).pack(anchor=W, pady=(5, 0))

        ttk.Separator(self).pack(fill=X, padx=20, pady=10)

        # Info de montos
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, padx=20)

        # Total del pedido
        row1 = ttk.Frame(info_frame)
        row1.pack(fill=X, pady=2)
        ttk.Label(row1, text="Total del pedido:", font=("Arial", 11)).pack(side=LEFT)
        ttk.Label(row1, text=f"${self.total:.2f}", font=("Arial", 11, "bold")).pack(side=RIGHT)

        # Ya pagado
        row2 = ttk.Frame(info_frame)
        row2.pack(fill=X, pady=2)
        ttk.Label(row2, text="Ya pagado:", font=("Arial", 11)).pack(side=LEFT)
        ttk.Label(
            row2,
            text=f"${self.already_paid:.2f}",
            font=("Arial", 11, "bold"),
            bootstyle="success" if self.already_paid > 0 else "secondary"
        ).pack(side=RIGHT)

        # Restante
        row3 = ttk.Frame(info_frame)
        row3.pack(fill=X, pady=2)
        ttk.Label(row3, text="Restante por pagar:", font=("Arial", 11, "bold")).pack(side=LEFT)
        ttk.Label(
            row3,
            text=f"${self.remaining:.2f}",
            font=("Arial", 11, "bold"),
            bootstyle="danger"
        ).pack(side=RIGHT)

        ttk.Separator(self).pack(fill=X, padx=20, pady=10)

        # Campo de pago
        payment_frame = ttk.Frame(self)
        payment_frame.pack(fill=X, padx=20)

        ttk.Label(
            payment_frame,
            text="Monto del pago:",
            font=("Arial", 11, "bold")
        ).pack(anchor=W)

        self.payment_var = ttk.StringVar(value=f"{self.remaining:.2f}")
        ttk.Entry(
            payment_frame,
            textvariable=self.payment_var,
            font=("Arial", 14),
            justify=CENTER
        ).pack(fill=X, pady=(5, 0), ipady=5)

        ttk.Separator(self).pack(fill=X, padx=20, pady=10)

        # Botones
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=(0, 20))

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.cancel,
            bootstyle="secondary-outline"
        ).pack(side=RIGHT, padx=(5, 0))

        ttk.Button(
            btn_frame,
            text="Confirmar Pago",
            command=self.confirm,
            bootstyle="success"
        ).pack(side=RIGHT)

    def confirm(self):
        try:
            payment = float(self.payment_var.get())
        except ValueError:
            mb.showwarning("Error", "Ingrese un monto válido", parent=self)
            return

        if payment < 0:
            mb.showwarning("Error", "El monto no puede ser negativo", parent=self)
            return

        if round(payment, 2) != round(self.remaining, 2):
            mb.showwarning(
                "Monto incorrecto",
                f"El monto debe ser exactamente ${self.remaining:.2f} para completar el pedido.",
                parent=self
            )
            return

        self.result = payment
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    def center_on_parent(self, parent):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")


class PaymentRegisterDialog(ttk.Toplevel):
    """Dialogo modal para registrar un abono/pago parcial a un pedido."""

    def __init__(self, parent, order_data, remaining):
        super().__init__(parent)
        self.result = None  # None = cancelado, float = monto del abono

        self.total = order_data['total']
        self.already_paid = order_data.get('amount_paid', 0.0) or 0.0
        self.remaining = remaining

        self.title(f"Registrar Pago - Pedido #{order_data['id']}")
        self.geometry("400x320")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.setup_ui(order_data)
        self.center_on_parent(parent)

    def setup_ui(self, order_data):
        header = ttk.Frame(self)
        header.pack(fill=X, padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text=f"Registrar Pago - Pedido #{order_data['id']}",
            font=("Arial", 14, "bold")
        ).pack(anchor=W)

        ttk.Separator(self).pack(fill=X, padx=20, pady=10)

        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, padx=20)

        row1 = ttk.Frame(info_frame)
        row1.pack(fill=X, pady=2)
        ttk.Label(row1, text="Total:", font=("Arial", 11)).pack(side=LEFT)
        ttk.Label(row1, text=f"${self.total:.2f}", font=("Arial", 11, "bold")).pack(side=RIGHT)

        row2 = ttk.Frame(info_frame)
        row2.pack(fill=X, pady=2)
        ttk.Label(row2, text="Ya pagado:", font=("Arial", 11)).pack(side=LEFT)
        ttk.Label(row2, text=f"${self.already_paid:.2f}", font=("Arial", 11, "bold"), bootstyle="success").pack(side=RIGHT)

        row3 = ttk.Frame(info_frame)
        row3.pack(fill=X, pady=2)
        ttk.Label(row3, text="Restante:", font=("Arial", 11, "bold")).pack(side=LEFT)
        ttk.Label(row3, text=f"${self.remaining:.2f}", font=("Arial", 11, "bold"), bootstyle="danger").pack(side=RIGHT)

        ttk.Separator(self).pack(fill=X, padx=20, pady=10)

        payment_frame = ttk.Frame(self)
        payment_frame.pack(fill=X, padx=20)

        ttk.Label(payment_frame, text="Monto a abonar:", font=("Arial", 11, "bold")).pack(anchor=W)

        self.payment_var = ttk.StringVar()
        self.payment_entry = ttk.Entry(
            payment_frame, textvariable=self.payment_var,
            font=("Arial", 14), justify=CENTER
        )
        self.payment_entry.pack(fill=X, pady=(5, 0), ipady=5)
        self.payment_entry.focus_set()

        ttk.Separator(self).pack(fill=X, padx=20, pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=20, pady=(0, 20))

        ttk.Button(btn_frame, text="Cancelar", command=self.cancel, bootstyle="secondary-outline").pack(side=RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Registrar Abono", command=self.confirm, bootstyle="success").pack(side=RIGHT)

    def confirm(self):
        try:
            amount = float(self.payment_var.get())
        except ValueError:
            mb.showwarning("Error", "Ingrese un monto válido", parent=self)
            return

        if amount <= 0:
            mb.showwarning("Error", "El monto debe ser mayor a 0", parent=self)
            return

        if round(amount, 2) > round(self.remaining, 2):
            mb.showwarning("Error", f"El monto no puede exceder el restante (${self.remaining:.2f})", parent=self)
            return

        self.result = amount
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    def center_on_parent(self, parent):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")
