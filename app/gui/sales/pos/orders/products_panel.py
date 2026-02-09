import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ProductsPanel(ttk.Labelframe):
    def __init__(self, parent, on_product_added):

        super().__init__(parent, text="  Productos - Seleccione un cliente  ", padding=10)
        self.on_product_added = on_product_added
        self.products_list = []
        self.product_widgets = {}

        self.setup_ui()

    def setup_ui(self):

        # Initial message (without selected client)
        self.no_customer_label = ttk.Label(
            self,
            text="Seleccione un cliente para ver los productos",
            font=("Arial", 14),
            bootstyle="secondary"
        )
        self.no_customer_label.pack(expand=YES)

        # Product frame (initially hidden)
        self.content_frame = ttk.Frame(self)

        # Canvas for products with scroll
        canvas_frame = ttk.Frame(self.content_frame)
        canvas_frame.pack(fill=BOTH, expand=YES)

        self.canvas = ttk.Canvas(canvas_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.scrollbar.pack(side=RIGHT, fill=Y)

    def load(self, products):
        self.products_list = products

    def show_for_customer(self, customer_name):
        self.config(text=f"  Productos para: {customer_name}  ")
        self.no_customer_label.pack_forget()
        self.content_frame.pack(fill=BOTH, expand=YES)
        self._display_products()

    def hide_products(self):
        self.config(text="  Productos - Seleccione un cliente  ")
        self.content_frame.pack_forget()
        self.no_customer_label.pack(expand=YES)

    def _display_products(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.product_widgets = {}

        for product_id, icon, name, default_price in self.products_list:
            self._create_card(product_id, icon, name, default_price)

    def _create_card(self, product_id, icon, name, default_price):
        card = ttk.Frame(self.inner_frame, bootstyle="light", relief="solid", borderwidth=1)
        card.pack(fill=X, pady=4, padx=2)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=15, pady=12)

        # Top row: name and base price
        top_row = ttk.Frame(content)
        top_row.pack(fill=X)

        ttk.Label(
            top_row, text=f"{icon or '🍴'} {name}", font=("Arial", 13, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            top_row, text=f"Precio base: ${default_price:.2f}",
            font=("Arial", 10), bootstyle="secondary"
        ).pack(side=RIGHT)

        # Bottom row: controls
        controls_row = ttk.Frame(content)
        controls_row.pack(fill=X, pady=(10, 0))

        price_frame = ttk.Frame(controls_row)
        price_frame.pack(side=LEFT)

        ttk.Label(price_frame, text="Precio: $").pack(side=LEFT)

        price_var = ttk.StringVar(value=str(default_price))
        ttk.Entry(price_frame, textvariable=price_var, width=8, font=("Arial", 11)).pack(side=LEFT)

        qty_frame = ttk.Frame(controls_row)
        qty_frame.pack(side=LEFT, padx=(20, 0))

        ttk.Label(qty_frame, text="Cantidad:").pack(side=LEFT)

        qty_var = ttk.StringVar(value="1")
        ttk.Entry(qty_frame, textvariable=qty_var, width=5, font=("Arial", 11)).pack(side=LEFT, padx=(5, 0))

        ttk.Button(
            controls_row,
            text="+ Agregar",
            command=lambda: self.on_product_added(product_id, name, price_var, qty_var),
            bootstyle="success-outline"
        ).pack(side=RIGHT)

        self.product_widgets[product_id] = {
            'price_var': price_var,
            'qty_var': qty_var,
            'default_price': default_price
        }

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
