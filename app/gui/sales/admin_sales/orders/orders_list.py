import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.constants import ORDER_STATUSES


class OrdersList(ttk.Labelframe):
    def __init__(self, parent, customers_cache, on_select):
        super().__init__(parent, text="  Lista de Pedidos  ", padding=10)
        self.customers_cache = customers_cache
        self.on_select = on_select

        self.setup_ui()

    def setup_ui(self):
        list_canvas_frame = ttk.Frame(self)
        list_canvas_frame.pack(fill=BOTH, expand=YES)

        self.list_canvas = ttk.Canvas(list_canvas_frame, highlightthickness=0)
        self.list_scrollbar = ttk.Scrollbar(list_canvas_frame, orient=VERTICAL, command=self.list_canvas.yview)

        self.list_inner_frame = ttk.Frame(self.list_canvas)
        self.list_canvas_window = self.list_canvas.create_window((0, 0), window=self.list_inner_frame, anchor="nw")

        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)

        self.list_inner_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )
        self.list_canvas.bind(
            "<Configure>",
            lambda e: self.list_canvas.itemconfig(self.list_canvas_window, width=e.width)
        )

        self.list_canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.list_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.list_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.list_scrollbar.pack(side=RIGHT, fill=Y)

    def display_orders(self, orders):
        for widget in self.list_inner_frame.winfo_children():
            widget.destroy()

        if not orders:
            ttk.Label(
                self.list_inner_frame,
                text="No hay pedidos",
                font=("Arial", 12),
                bootstyle="secondary"
            ).pack(pady=40)
            return

        for order in orders:
            self.create_order_card(order)

    def create_order_card(self, order):
        status_info = ORDER_STATUSES.get(order.status, {"label": order.status, "color": "secondary"})

        card = ttk.Frame(
            self.list_inner_frame,
            bootstyle=status_info['color'],
            relief="solid",
            borderwidth=2
        )
        card.pack(fill=X, pady=4)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=12, pady=10)

        # Fila superior: ID y fecha
        top_row = ttk.Frame(content)
        top_row.pack(fill=X)

        ttk.Label(
            top_row,
            text=f"Pedido #{order.id}",
            font=("Arial", 13, "bold")
        ).pack(side=LEFT)

        date_str = order.date.strftime("%d/%m/%Y %H:%M") if order.date else "N/A"
        ttk.Label(
            top_row,
            text=date_str,
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        # Cliente
        customer_name = self.customers_cache.get(order.customer_id, "Cliente desconocido")
        ttk.Label(
            content,
            text=f"Cliente: {customer_name}",
            font=("Arial", 10)
        ).pack(anchor=W, pady=(5, 0))

        # Fila inferior: Total y estado
        bottom_row = ttk.Frame(content)
        bottom_row.pack(fill=X, pady=(8, 0))

        ttk.Label(
            bottom_row,
            text=f"${order.total:.2f}",
            font=("Arial", 14, "bold"),
            bootstyle="success"
        ).pack(side=LEFT)

        ttk.Label(
            bottom_row,
            text=f"  {status_info['label']}  ",
            font=("Arial", 9, "bold"),
            bootstyle=f"inverse-{status_info['color']}"
        ).pack(side=RIGHT)

        # Hacer clickeable
        for widget in [card, content]:
            widget.bind("<Button-1>", lambda e, o=order: self.on_select(o))
            widget.configure(cursor="hand2")

    # --- Mousewheel ---

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.list_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.list_canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        self.list_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.list_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.list_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.list_canvas.unbind_all("<MouseWheel>")
        self.list_canvas.unbind_all("<Button-4>")
        self.list_canvas.unbind_all("<Button-5>")
