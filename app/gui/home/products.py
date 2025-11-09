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
        for producto_id, nombre, precio in self.content.products_items:
            self.product_card(producto_id, nombre, precio)
    
    def product_card(self, product_id, name, price):

        card = ttk.Frame(
            self.scrollable_frame,
            bootstyle="light",
            relief="solid",
            borderwidth=1
        )
        card.pack(fill=BOTH, expand=YES, pady=8)
    
        emoji = self.get_emoji(name)

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
        
        # Botón agregar
        btn_agregar = ttk.Button(
            card,
            text="Agregar al Carrito",
            command=lambda: self.content.add_product_to_car({
                'id': product_id,
                'name': name,
                'price': price
            }),
            bootstyle="primary",
            width=18
        )
        btn_agregar.pack(side=RIGHT, padx=15, pady=15)
    
    def get_emoji(self, name):
        """Obtener emoji según el nombre del producto"""
        lower_name = name.lower()
        
        if "tortilla" in lower_name:
            return "🌮"
        elif "tostada" in lower_name:
            return "🍞"
        elif "tlayuda" in lower_name:
            return "🌯"
        elif "sope" in lower_name:
            return "🥙"
        elif "tamal" in lower_name:
            return "🥟"
        elif "salsa" in lower_name:
            return "🍅"
        elif "queso" in lower_name or "quesadilla" in lower_name:
            return "🧀"
        elif "frijol" in lower_name:
            return "🥜"
        elif "gorditas" in lower_name:
            return "🌕"
        else:
            return "🍴"

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