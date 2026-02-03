import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class Products(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content

        self.setup_ui()
        self.content.get_products()
        self.show_products()
    
    def setup_ui(self):

        # Container with scroll
        self.container = ttk.Frame(self)
        self.container.pack(fill=BOTH, expand=YES)

        self.tile_gui()

        # Frame con scrollbar
        self.products_gui()

    def tile_gui(self):

        # tile section
        self.titulo = ttk.Label(
            self.container,
            text="📦 PRODUCTOS",
            font=("Arial", 20, "bold")
        )
        self.titulo.pack(pady=10)

    def products_gui(self):
        canvas_frame = ttk.Frame(self.container)
        canvas_frame.pack(fill=BOTH, expand=YES)

        # Canvas y scrollbar
        self.canvas = ttk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Configurar para que el scrollable_frame ocupe el ancho del canvas
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # Enable mouse wheel scrolling
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def show_products(self):
        """Mostrar productos en cards"""
        # Limpiar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Crear card para cada producto
        for producto_id, icon, nombre, precio in self.content.products_items:
            self.product_card(producto_id, icon, nombre, precio)

    def product_card(self, product_id, icon, name, price):

        card = ttk.Frame(
            self.scrollable_frame,
            bootstyle="light",
            relief="solid",
            borderwidth=1
        )
        card.pack(fill=BOTH, expand=YES, pady=8)

        emoji = icon or "🍴"

        lbl_emoji = ttk.Label(
            card,
            text=emoji,
            font=("Arial", 45)
        )
        lbl_emoji.pack(side=LEFT, padx=(15, 5), pady=15)

        # Información del producto
        info_frame = ttk.Frame(card)
        info_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(5, 15), pady=15)
        
        lbl_nombre = ttk.Label(
            info_frame,
            text=name,
            font=("Arial", 16, "bold")
        )
        lbl_nombre.pack(anchor=W)
        
        lbl_precio = ttk.Label(
            info_frame,
            text=f"${price:.2f}",
            font=("Arial", 18),
            bootstyle="success"
        )
        lbl_precio.pack(anchor=W, pady=(5, 0))
        
        # Quantity selector: [ − ] qty [ + ]
        qty_frame = ttk.Frame(card)
        qty_frame.pack(side=RIGHT, padx=15, pady=15)

        current_qty = self._get_cart_qty(product_id)

        ttk.Button(
            qty_frame,
            text="−",
            command=lambda pid=product_id: self._decrement(pid),
            bootstyle="danger-outline",
            width=3,
            state="normal" if current_qty > 0 else "disabled"
        ).pack(side=LEFT, ipady=8)

        ttk.Label(
            qty_frame,
            text=str(current_qty),
            font=("Arial", 18, "bold"),
            width=3,
            anchor="center"
        ).pack(side=LEFT, padx=8)

        ttk.Button(
            qty_frame,
            text="+",
            command=lambda pid=product_id, n=name, p=price: self._increment(pid, n, p),
            bootstyle="success",
            width=3
        ).pack(side=LEFT, ipady=8)

    def _get_cart_qty(self, product_id):
        for item in self.content.shopping_cart:
            if item['id'] == product_id:
                return item['quantity']
        return 0

    def _increment(self, product_id, name, price):
        self.content.add_product_to_car({'id': product_id, 'name': name, 'price': price})
        self.show_products()

    def _decrement(self, product_id):
        self.content.remove_one_from_car(product_id)
        self.show_products()

    # mouse events

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Windows uses event.delta, Linux/Mac use event.num
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")


    def _bind_mousewheel(self):
        """Bind mouse wheel events when mouse enters canvas"""
        # Windows and MacOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)


    def _unbind_mousewheel(self):
        """Unbind mouse wheel events when mouse leaves canvas"""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")