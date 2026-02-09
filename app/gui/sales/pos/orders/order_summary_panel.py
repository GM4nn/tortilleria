import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class OrderSummaryPanel(ttk.Frame):
    def __init__(self, parent, on_save, on_clear, on_remove_item):
        super().__init__(parent, width=320)
        self.on_save = on_save
        self.on_clear = on_clear
        self.on_remove_item = on_remove_item

        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):

        self.setup_gui_title()
        self.setup_gui_items()
        self.setup_gui_btn_actions()

    def setup_gui_title(self):
        ttk.Label(self, text="Resumen del Pedido", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        # Selected client
        self.customer_frame = ttk.Labelframe(self, text="Cliente", padding=10)
        self.customer_frame.pack(fill=X, pady=(0, 10))

        self.customer_label = ttk.Label(
            self.customer_frame,
            text="Ninguno seleccionado",
            font=("Arial", 11),
            bootstyle="secondary"
        )
        self.customer_label.pack()

        total_frame = ttk.Frame(self, bootstyle="dark", relief="solid", borderwidth=2)
        total_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            total_frame, text="TOTAL", font=("Arial", 12), bootstyle="inverse-dark"
        ).pack(pady=(10, 0))

        self.total_label = ttk.Label(
            total_frame, text="$0.00", font=("Arial", 32, "bold"), bootstyle="inverse-dark"
        )
        self.total_label.pack(pady=(5, 10))

    def setup_gui_items(self):
        
        items_frame = ttk.Labelframe(self, text="Items del pedido", padding=5)
        items_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))

        self.items_canvas = ttk.Canvas(items_frame, highlightthickness=0)
        self.items_scrollbar = ttk.Scrollbar(
            items_frame, orient=VERTICAL, command=self.items_canvas.yview
        )

        self.items_inner_frame = ttk.Frame(self.items_canvas)
        self.items_canvas_window = self.items_canvas.create_window(
            (0, 0), window=self.items_inner_frame, anchor="nw"
        )

        self.items_canvas.configure(yscrollcommand=self.items_scrollbar.set)

        self.items_inner_frame.bind(
            "<Configure>",
            lambda e: self.items_canvas.configure(scrollregion=self.items_canvas.bbox("all"))
        )
        self.items_canvas.bind(
            "<Configure>",
            lambda e: self.items_canvas.itemconfig(self.items_canvas_window, width=e.width)
        )

        self.items_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.items_scrollbar.pack(side=RIGHT, fill=Y)

        # Mensaje sin items
        self.no_items_label = ttk.Label(
            self.items_inner_frame,
            text="Sin productos",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.no_items_label.pack(pady=20)

    def setup_gui_btn_actions(self):

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X)

        self.btn_save = ttk.Button(
            btn_frame, text="Guardar Pedido", command=self.on_save,
            bootstyle="success", state=DISABLED
        )
        self.btn_save.pack(fill=X, pady=5, ipady=10)

        self.btn_clear = ttk.Button(
            btn_frame, text="Limpiar", command=self.on_clear,
            bootstyle="danger-outline"
        )
        self.btn_clear.pack(fill=X, pady=5, ipady=5)

    def set_customer(self, name):
        self.customer_label.config(text=name, bootstyle="success")

    def clear_customer(self):
        self.customer_label.config(text="Ninguno seleccionado", bootstyle="secondary")

    def refresh(self, order_items):
        for widget in self.items_inner_frame.winfo_children():
            widget.destroy()

        if not order_items:
            ttk.Label(
                self.items_inner_frame, text="Sin productos",
                font=("Arial", 10), bootstyle="secondary"
            ).pack(pady=20)
            self.total_label.config(text="$0.00")
            return

        for i, item in enumerate(order_items):
            self._create_item_card(i, item)

        total = sum(item['subtotal'] for item in order_items)
        self.total_label.config(text=f"${total:.2f}")

    def set_save_enabled(self, enabled):
        self.btn_save.config(state=NORMAL if enabled else DISABLED)

    def _create_item_card(self, index, item):
        card = ttk.Frame(self.items_inner_frame, bootstyle="light")
        card.pack(fill=X, pady=2, padx=2)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=8, pady=6)

        info_frame = ttk.Frame(content)
        info_frame.pack(fill=X)

        ttk.Label(info_frame, text=item['name'], font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(
            info_frame, text=f"x{item['quantity']:.0f}",
            font=("Arial", 9), bootstyle="secondary"
        ).pack(side=RIGHT)

        price_frame = ttk.Frame(content)
        price_frame.pack(fill=X)

        ttk.Label(
            price_frame, text=f"${item['price']:.2f} c/u",
            font=("Arial", 9), bootstyle="secondary"
        ).pack(side=LEFT)

        ttk.Label(
            price_frame, text=f"${item['subtotal']:.2f}",
            font=("Arial", 10, "bold"), bootstyle="success"
        ).pack(side=RIGHT)

        ttk.Button(
            content, text="Eliminar",
            command=lambda: self.on_remove_item(index),
            bootstyle="danger-link", width=8
        ).pack(anchor=E, pady=(4, 0))
