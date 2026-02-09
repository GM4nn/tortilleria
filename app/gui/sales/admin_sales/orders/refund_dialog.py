import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *


class RefundDialog(ttk.Toplevel):
    """Dialogo modal para registrar devoluciones al completar un pedido."""

    def __init__(self, parent, order_data):
        super().__init__(parent)
        self.order_data = order_data
        self.result = None  # None = cancelado, list = datos de reembolso
        self.item_widgets = []

        self.title(f"Devoluciones - Pedido #{order_data['id']}")
        self.geometry("550x500")
        self.resizable(False, True)

        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.center_on_parent(parent)

    def setup_ui(self):
        # Header
        header = ttk.Frame(self)
        header.pack(fill=X, padx=15, pady=(15, 5))

        ttk.Label(
            header,
            text=f"Completar Pedido #{self.order_data['id']}",
            font=("Arial", 14, "bold")
        ).pack(anchor=W)

        ttk.Label(
            header,
            text="Ingrese la cantidad devuelta de cada producto (0 si no hubo devolución)",
            font=("Arial", 9),
            bootstyle="secondary",
            wraplength=500
        ).pack(anchor=W, pady=(5, 0))

        ttk.Separator(self).pack(fill=X, padx=15, pady=10)

        # Scrollable area para productos
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=BOTH, expand=YES, padx=15)

        canvas = ttk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=canvas.yview)

        inner_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width)
        )

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Crear fila por cada producto del pedido
        for detail in self.order_data['details']:
            self._create_product_row(inner_frame, detail)

        ttk.Separator(self).pack(fill=X, padx=15, pady=10)

        # Botones
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=15, pady=(0, 15))

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.cancel,
            bootstyle="secondary-outline"
        ).pack(side=RIGHT, padx=(5, 0))

        ttk.Button(
            btn_frame,
            text="Completar Pedido",
            command=self.confirm,
            bootstyle="success"
        ).pack(side=RIGHT)

    def _create_product_row(self, parent, detail):
        card = ttk.Frame(parent, bootstyle="light", relief="solid", borderwidth=1)
        card.pack(fill=X, pady=3)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=12, pady=10)

        # Info del producto
        info_row = ttk.Frame(content)
        info_row.pack(fill=X)

        ttk.Label(
            info_row,
            text=detail['product_name'],
            font=("Arial", 11, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            info_row,
            text=f"Pedido: {detail['quantity']:.0f}",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        # Controles
        controls_row = ttk.Frame(content)
        controls_row.pack(fill=X, pady=(8, 0))

        # Cantidad devuelta
        qty_frame = ttk.Frame(controls_row)
        qty_frame.pack(side=LEFT)

        ttk.Label(qty_frame, text="Cant. devuelta:", font=("Arial", 10)).pack(side=LEFT)

        qty_var = ttk.StringVar(value="0")
        ttk.Entry(
            qty_frame, textvariable=qty_var, width=6, font=("Arial", 11)
        ).pack(side=LEFT, padx=(5, 0))

        # Comentarios
        comment_frame = ttk.Frame(controls_row)
        comment_frame.pack(side=LEFT, padx=(15, 0), fill=X, expand=YES)

        ttk.Label(comment_frame, text="Nota:", font=("Arial", 10)).pack(side=LEFT)

        comment_var = ttk.StringVar()
        ttk.Entry(
            comment_frame, textvariable=comment_var, font=("Arial", 10)
        ).pack(side=LEFT, padx=(5, 0), fill=X, expand=YES)

        self.item_widgets.append({
            'product_id': detail['product_id'],
            'product_name': detail['product_name'],
            'max_quantity': detail['quantity'],
            'qty_var': qty_var,
            'comment_var': comment_var
        })

    def confirm(self):
        refund_items = []

        for widget in self.item_widgets:
            try:
                qty = float(widget['qty_var'].get())
            except ValueError:
                mb.showwarning(
                    "Error",
                    f"Ingrese un número válido para '{widget['product_name']}'",
                    parent=self
                )
                return

            if qty < 0:
                mb.showwarning(
                    "Error",
                    f"La cantidad devuelta de '{widget['product_name']}' no puede ser negativa",
                    parent=self
                )
                return

            refund_items.append({
                'product_id': widget['product_id'],
                'quantity': qty,
                'comments': widget['comment_var'].get().strip() or None
            })

        self.result = refund_items
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
