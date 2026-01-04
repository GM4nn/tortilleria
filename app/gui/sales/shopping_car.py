
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.customers import customer_provider


class ShoppingCar(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent, width=350)
        self.app = app
        self.content = content
        self.selected_customer = None  # Cliente seleccionado
        self.customers_list = []  # Lista de todos los clientes

        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del panel derecho"""
        
        # Header Section
        self.section_total_price()
        
        # Frame with scrollbar to shopping car items
        self.section_shopping_car_items()
        
        # Action Buttons
        self.action_buttons()


    def section_total_price(self):

        title = ttk.Label(
            self,
            text="🛒 CARRITO",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)
        
        # Frame del total (arriba)
        self.frame_total = ttk.Frame(
            self,
            bootstyle="dark",
            relief="solid",
            borderwidth=2
        )
        self.frame_total.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(
            self.frame_total,
            text="TOTAL",
            font=("Arial", 12),
            bootstyle="inverse-dark"
        ).pack(pady=(10, 0))
        
        self.lbl_total = ttk.Label(
            self.frame_total,
            text="$0.00",
            font=("Arial", 36, "bold"),
            bootstyle="inverse-dark"
        )
        self.lbl_total.pack(pady=(5, 10))


    def section_shopping_car_items(self):
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=BOTH, expand=YES, padx=10)

        self._create_canvas()


    def _create_canvas(self):
        """Create or recreate the canvas with scrollbar"""
        # Canvas and scrollbar
        self.canvas = ttk.Canvas(self.canvas_frame, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient=VERTICAL, command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Update scroll region properly
        def _on_frame_configure(event):
            # Get the bounding box of all content
            bbox = self.canvas.bbox("all")
            if bbox:
                # Only allow scrolling if content is taller than canvas
                canvas_height = self.canvas.winfo_height()
                content_height = bbox[3]  # bbox is (x1, y1, x2, y2)

                if content_height > canvas_height:
                    # Content is larger, allow scrolling
                    self.canvas.configure(scrollregion=bbox)
                else:
                    # Content is smaller, set scrollregion to canvas size to prevent scroll
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], canvas_height))

        self.scrollable_frame.bind("<Configure>", _on_frame_configure)

        # Adjust scrollable_frame width to canvas
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            # Also update scrollregion when canvas resizes
            bbox = self.canvas.bbox("all")
            if bbox:
                canvas_height = event.height
                content_height = bbox[3]
                if content_height > canvas_height:
                    self.canvas.configure(scrollregion=bbox)
                else:
                    self.canvas.configure(scrollregion=(0, 0, bbox[2], canvas_height))

        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Enable mouse wheel scrolling
        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.lbl_vacio = ttk.Label(
            self.scrollable_frame,
            text="Carrito vacío 🛒",
            font=("Arial", 20),
            bootstyle="secondary"
        )
        self.lbl_vacio.pack(pady=(0, 10))


    def action_buttons(self):
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=10)

        # Customer Search Section
        customer_frame = ttk.Labelframe(btn_frame, text="Cliente", padding=10)
        customer_frame.pack(fill=X, pady=(0, 10))

        # Search box
        search_frame = ttk.Frame(customer_frame)
        search_frame.pack(fill=X, pady=(0, 5))

        self.customer_search_var = ttk.StringVar()
        self.customer_search_var.trace_add('write', self.on_search_change)

        self.customer_search_entry = ttk.Entry(
            search_frame,
            textvariable=self.customer_search_var,
            font=("Arial", 10)
        )
        self.customer_search_entry.pack(side=LEFT, fill=X, expand=True)

        # Selected customer display
        self.selected_customer_label = ttk.Label(
            customer_frame,
            text="Cliente: Mostrador (Por defecto)",
            font=("Arial", 9),
            bootstyle="secondary"
        )
        self.selected_customer_label.pack(fill=X)

        # Dropdown with search results (initially hidden)
        self.customer_dropdown_frame = ttk.Frame(customer_frame)
        self.customer_listbox = None

        self.btn_charge = ttk.Button(
            btn_frame,
            text="💰 COBRAR",
            command=self.content.charge,
            bootstyle="success",
        )
        self.btn_charge.pack(fill=X, pady=5, ipady=12)
        
        self.btn_clean = ttk.Button(
            btn_frame,
            text="🗑️ Limpiar",
            command=self.content.clean_shopping_car,
            bootstyle="danger",
        )
        self.btn_clean.pack(fill=X, pady=5, ipady=8)

        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.lbl_items = ttk.Label(
            info_frame,
            text="0 Productos",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.lbl_items.pack()


    def refresh_shopping_car(self):

        # Destroy scrollable_frame, canvas and scrollbar completely
        if hasattr(self, 'scrollable_frame'):
            self.scrollable_frame.destroy()
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()

        # Recreate canvas from scratch (scroll resets automatically)
        self._create_canvas()

        # Reset scroll to top after recreation
        self.canvas.yview_moveto(0)

        if not self.content.shopping_cart:
            self.lbl_total.config(text="$0.00")
            self.lbl_items.config(text="0 items")
            # Reset customer selection when cart is empty
            self.selected_customer = None
            self.selected_customer_label.config(
                text="Cliente: Mostrador (Por defecto)",
                bootstyle="secondary"
            )
            return

        # Remove the empty label
        self.lbl_vacio.destroy()

        for i, item in enumerate(self.content.shopping_cart):
            self.create_shopping_car_item(i, item)

        # update total
        total = self.content.get_total()
        self.lbl_total.config(text=f"${total:.2f}")

        # update contador
        total_items = sum(item['quantity'] for item in self.content.shopping_cart)
        self.lbl_items.config(text=f"{total_items} items")


    def create_shopping_car_item(self, index, item):

        item_frame = ttk.Frame(
            self.scrollable_frame,
            bootstyle="light",
            relief="solid",
            borderwidth=1
        )
        # First item has no top padding, rest have 5px top padding
        pady = (0, 5) if index == 0 else 5
        item_frame.pack(fill=X, expand=NO, pady=pady, padx=0)

        content_frame = ttk.Frame(item_frame)
        content_frame.pack(fill=X, expand=YES, padx=10, pady=10)

        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill=X, expand=YES)

        ttk.Label(
            header_frame,
            text=item['name'],
            font=("Arial", 11, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            header_frame,
            text=f"x{item['quantity']}",
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        price_frame = ttk.Frame(content_frame)
        price_frame.pack(fill=X, expand=YES, pady=(5, 0))

        ttk.Label(
            price_frame,
            text=f"${item['price']:.2f} c/u",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=LEFT)

        ttk.Label(
            price_frame,
            text=f"${item['subtotal']:.2f}",
            font=("Arial", 12, "bold"),
            bootstyle="success"
        ).pack(side=RIGHT)

        btn_eliminar = ttk.Button(
            content_frame,
            text="❌ Eliminar",
            command=lambda: self.content.delete_product_from_car(index),
            bootstyle="danger-outline"
        )
        btn_eliminar.pack(fill=X, pady=(8, 0))


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

    def load_customers(self):
        """Cargar todos los clientes (excluyendo los ocultos)"""
        self.customers_list = customer_provider.get_all()

    def on_search_change(self, *args):
        """Manejar cambios en el campo de búsqueda"""
        search_text = self.customer_search_var.get().lower()

        # Si está vacío, ocultar el dropdown
        if not search_text:
            self.hide_customer_dropdown()
            return

        # Cargar clientes si no están cargados
        if not self.customers_list:
            self.load_customers()

        # Filtrar clientes
        filtered_customers = [
            c for c in self.customers_list
            if search_text in c.customer_name.lower()
        ]

        # Mostrar resultados
        self.show_customer_dropdown(filtered_customers)

    def show_customer_dropdown(self, customers):
        """Mostrar dropdown con resultados de búsqueda"""
        # Limpiar dropdown anterior
        self.hide_customer_dropdown()

        if not customers:
            return

        # Mostrar frame del dropdown
        self.customer_dropdown_frame.pack(fill=X, pady=(5, 0))

        # Crear listbox con resultados
        self.customer_listbox = ttk.Treeview(
            self.customer_dropdown_frame,
            columns=(),
            show="tree",
            height=min(5, len(customers))
        )
        self.customer_listbox.pack(fill=BOTH, expand=False)
        # Configurar columna sin ancho fijo para que se ajuste al contenedor
        self.customer_listbox.column("#0", width=0, stretch=True)

        # Agregar clientes al listbox
        for customer in customers:
            # Guardar el ID en tags para recuperarlo después
            self.customer_listbox.insert(
                "",
                "end",
                text=customer.customer_name,
                tags=(str(customer.id),)
            )

        # Bind para selección
        self.customer_listbox.bind("<<TreeviewSelect>>", self.on_customer_select)

    def hide_customer_dropdown(self):
        """Ocultar dropdown de clientes"""
        if self.customer_listbox:
            self.customer_listbox.destroy()
            self.customer_listbox = None
        self.customer_dropdown_frame.pack_forget()

    def on_customer_select(self, event):
        """Manejar selección de cliente"""
        if not self.customer_listbox:
            return

        selection = self.customer_listbox.selection()
        if not selection:
            return

        # Obtener el cliente seleccionado
        item = self.customer_listbox.item(selection[0])
        customer_id = int(item['tags'][0])  # Obtener ID desde tags
        customer_name = item['text']

        # Buscar el cliente completo en la lista
        for customer in self.customers_list:
            if customer.id == customer_id:
                self.selected_customer = customer
                break

        # Actualizar label
        self.selected_customer_label.config(
            text=f"Cliente: {customer_name}",
            bootstyle="success"
        )

        # Limpiar búsqueda y ocultar dropdown
        self.customer_search_var.set("")
        self.hide_customer_dropdown()

    def get_selected_customer_id(self):
        """Obtener el ID del cliente seleccionado o el cliente Mostrador por defecto"""
        if self.selected_customer:
            return self.selected_customer.id
        else:
            # Obtener el cliente Mostrador genérico
            mostrador = customer_provider.get_by_category('Mostrador')
            return mostrador.id if mostrador else None