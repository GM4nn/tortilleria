import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.data.providers.customers import customer_provider
from app.data.providers.inventory import inventory_provider
from app.data.providers.orders import order_provider


class OrderTab(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content
        self.selected_customer = None
        self.customers_list = []
        self.products_list = []
        self.order_items = []  # Items del pedido actual
        self.product_widgets = {}  # Para guardar referencias a los widgets de productos

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Panel principal dividido en 3 secciones
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Panel izquierdo: Lista de clientes
        self.setup_customers_panel()

        # Panel central: Productos con precios personalizados
        self.setup_products_panel()

        # Panel derecho: Resumen del pedido
        self.setup_order_summary_panel()

    def setup_customers_panel(self):
        """Panel izquierdo con lista de clientes"""
        self.customers_frame = ttk.Labelframe(
            self.main_container,
            text="  Seleccionar Cliente  ",
            padding=10,
            width=280
        )
        self.customers_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        self.customers_frame.pack_propagate(False)

        # Barra de búsqueda
        search_frame = ttk.Frame(self.customers_frame)
        search_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT)

        self.customer_search_var = ttk.StringVar()
        self.customer_search_var.trace_add('write', self.filter_customers)

        self.customer_search_entry = ttk.Entry(
            search_frame,
            textvariable=self.customer_search_var
        )
        self.customer_search_entry.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

        # Lista de clientes con scroll
        list_frame = ttk.Frame(self.customers_frame)
        list_frame.pack(fill=BOTH, expand=YES)

        self.customers_canvas = ttk.Canvas(list_frame, highlightthickness=0)
        self.customers_scrollbar = ttk.Scrollbar(
            list_frame, orient=VERTICAL, command=self.customers_canvas.yview
        )

        self.customers_inner_frame = ttk.Frame(self.customers_canvas)
        self.customers_canvas_window = self.customers_canvas.create_window(
            (0, 0), window=self.customers_inner_frame, anchor="nw"
        )

        self.customers_canvas.configure(yscrollcommand=self.customers_scrollbar.set)

        self.customers_inner_frame.bind(
            "<Configure>",
            lambda e: self.customers_canvas.configure(scrollregion=self.customers_canvas.bbox("all"))
        )
        self.customers_canvas.bind(
            "<Configure>",
            lambda e: self.customers_canvas.itemconfig(self.customers_canvas_window, width=e.width)
        )

        # Mouse wheel
        self.customers_canvas.bind("<Enter>", lambda e: self._bind_mousewheel_customers())
        self.customers_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel_customers())

        self.customers_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.customers_scrollbar.pack(side=RIGHT, fill=Y)

    def setup_products_panel(self):
        """Panel central con productos y precios personalizados"""
        self.products_frame = ttk.Labelframe(
            self.main_container,
            text="  Productos - Seleccione un cliente  ",
            padding=10
        )
        self.products_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Mensaje inicial
        self.no_customer_label = ttk.Label(
            self.products_frame,
            text="Seleccione un cliente para ver los productos",
            font=("Arial", 14),
            bootstyle="secondary"
        )
        self.no_customer_label.pack(expand=YES)

        # Frame para productos (inicialmente oculto)
        self.products_content_frame = ttk.Frame(self.products_frame)

        # Canvas para productos con scroll
        self.products_canvas_frame = ttk.Frame(self.products_content_frame)
        self.products_canvas_frame.pack(fill=BOTH, expand=YES)

        self.products_canvas = ttk.Canvas(self.products_canvas_frame, highlightthickness=0)
        self.products_scrollbar = ttk.Scrollbar(
            self.products_canvas_frame, orient=VERTICAL, command=self.products_canvas.yview
        )

        self.products_inner_frame = ttk.Frame(self.products_canvas)
        self.products_canvas_window = self.products_canvas.create_window(
            (0, 0), window=self.products_inner_frame, anchor="nw"
        )

        self.products_canvas.configure(yscrollcommand=self.products_scrollbar.set)

        self.products_inner_frame.bind(
            "<Configure>",
            lambda e: self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))
        )
        self.products_canvas.bind(
            "<Configure>",
            lambda e: self.products_canvas.itemconfig(self.products_canvas_window, width=e.width)
        )

        # Mouse wheel
        self.products_canvas.bind("<Enter>", lambda e: self._bind_mousewheel_products())
        self.products_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel_products())

        self.products_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.products_scrollbar.pack(side=RIGHT, fill=Y)

    def setup_order_summary_panel(self):
        """Panel derecho con resumen del pedido"""
        self.summary_frame = ttk.Frame(self.main_container, width=320)
        self.summary_frame.pack(side=LEFT, fill=Y)
        self.summary_frame.pack_propagate(False)

        # Título
        ttk.Label(
            self.summary_frame,
            text="Resumen del Pedido",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # Cliente seleccionado
        self.selected_customer_frame = ttk.Labelframe(
            self.summary_frame, text="Cliente", padding=10
        )
        self.selected_customer_frame.pack(fill=X, pady=(0, 10))

        self.selected_customer_label = ttk.Label(
            self.selected_customer_frame,
            text="Ninguno seleccionado",
            font=("Arial", 11),
            bootstyle="secondary"
        )
        self.selected_customer_label.pack()

        # Total
        self.total_frame = ttk.Frame(
            self.summary_frame,
            bootstyle="dark",
            relief="solid",
            borderwidth=2
        )
        self.total_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            self.total_frame,
            text="TOTAL",
            font=("Arial", 12),
            bootstyle="inverse-dark"
        ).pack(pady=(10, 0))

        self.total_label = ttk.Label(
            self.total_frame,
            text="$0.00",
            font=("Arial", 32, "bold"),
            bootstyle="inverse-dark"
        )
        self.total_label.pack(pady=(5, 10))

        # Lista de items del pedido
        items_frame = ttk.Labelframe(
            self.summary_frame, text="Items del pedido", padding=5
        )
        items_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))

        # Canvas para items con scroll
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

        # Mensaje cuando no hay items
        self.no_items_label = ttk.Label(
            self.items_inner_frame,
            text="Sin productos",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.no_items_label.pack(pady=20)

        # Botones de acción
        btn_frame = ttk.Frame(self.summary_frame)
        btn_frame.pack(fill=X)

        self.btn_save_order = ttk.Button(
            btn_frame,
            text="Guardar Pedido",
            command=self.save_order,
            bootstyle="success",
            state=DISABLED
        )
        self.btn_save_order.pack(fill=X, pady=5, ipady=10)

        self.btn_clear = ttk.Button(
            btn_frame,
            text="Limpiar",
            command=self.clear_order,
            bootstyle="danger-outline"
        )
        self.btn_clear.pack(fill=X, pady=5, ipady=5)

    def load_data(self):
        """Cargar clientes y productos"""
        self.customers_list = customer_provider.get_all()
        self.products_list = inventory_provider.get_all()
        self.display_customers()

    def display_customers(self, filter_text=""):
        """Mostrar lista de clientes"""
        # Limpiar lista actual
        for widget in self.customers_inner_frame.winfo_children():
            widget.destroy()

        filtered = self.customers_list
        if filter_text:
            filtered = [
                c for c in self.customers_list
                if filter_text.lower() in (c.customer_name or '').lower()
            ]

        if not filtered:
            ttk.Label(
                self.customers_inner_frame,
                text="No se encontraron clientes",
                bootstyle="secondary"
            ).pack(pady=20)
            return

        for customer in filtered:
            self.create_customer_card(customer)

    def create_customer_card(self, customer):
        """Crear tarjeta de cliente"""
        is_selected = self.selected_customer and self.selected_customer.id == customer.id
        style = "info" if is_selected else "light"

        card = ttk.Frame(
            self.customers_inner_frame,
            bootstyle=style,
            relief="solid",
            borderwidth=1
        )
        card.pack(fill=X, pady=2)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=10, pady=8)

        # Nombre del cliente
        name_label = ttk.Label(
            content,
            text=customer.customer_name,
            font=("Arial", 11, "bold")
        )
        name_label.pack(anchor=W)

        # Categoría
        if customer.customer_category:
            cat_label = ttk.Label(
                content,
                text=customer.customer_category,
                font=("Arial", 9),
                bootstyle="secondary"
            )
            cat_label.pack(anchor=W)

        # Hacer clickeable
        for widget in [card, content, name_label]:
            widget.bind("<Button-1>", lambda e, c=customer: self.select_customer(c))
            widget.configure(cursor="hand2")

    def select_customer(self, customer):
        """Seleccionar un cliente"""
        self.selected_customer = customer

        # Actualizar UI
        self.selected_customer_label.config(
            text=customer.customer_name,
            bootstyle="success"
        )

        # Actualizar título del panel de productos
        self.products_frame.config(text=f"  Productos para: {customer.customer_name}  ")

        # Mostrar panel de productos
        self.no_customer_label.pack_forget()
        self.products_content_frame.pack(fill=BOTH, expand=YES)

        # Refrescar lista de clientes para mostrar selección
        self.display_customers(self.customer_search_var.get())

        # Mostrar productos
        self.display_products()

        # Habilitar botón si hay items
        self.update_save_button_state()

    def display_products(self):
        """Mostrar productos con campos de precio y cantidad"""
        # Limpiar productos actuales
        for widget in self.products_inner_frame.winfo_children():
            widget.destroy()

        self.product_widgets = {}

        for product_id, icon, name, default_price in self.products_list:
            self.create_product_card(product_id, icon, name, default_price)

    def create_product_card(self, product_id, icon, name, default_price):
        """Crear tarjeta de producto con controles de precio y cantidad"""
        card = ttk.Frame(
            self.products_inner_frame,
            bootstyle="light",
            relief="solid",
            borderwidth=1
        )
        card.pack(fill=X, pady=4, padx=2)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=15, pady=12)

        # Fila superior: nombre y precio por defecto
        top_row = ttk.Frame(content)
        top_row.pack(fill=X)

        ttk.Label(
            top_row,
            text=f"{icon or '🍴'} {name}",
            font=("Arial", 13, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            top_row,
            text=f"Precio base: ${default_price:.2f}",
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        # Fila inferior: controles
        controls_row = ttk.Frame(content)
        controls_row.pack(fill=X, pady=(10, 0))

        # Precio personalizado
        price_frame = ttk.Frame(controls_row)
        price_frame.pack(side=LEFT)

        ttk.Label(price_frame, text="Precio: $").pack(side=LEFT)

        price_var = ttk.StringVar(value=str(default_price))
        price_entry = ttk.Entry(
            price_frame,
            textvariable=price_var,
            width=8,
            font=("Arial", 11)
        )
        price_entry.pack(side=LEFT)

        # Cantidad
        qty_frame = ttk.Frame(controls_row)
        qty_frame.pack(side=LEFT, padx=(20, 0))

        ttk.Label(qty_frame, text="Cantidad:").pack(side=LEFT)

        qty_var = ttk.StringVar(value="1")
        qty_entry = ttk.Entry(
            qty_frame,
            textvariable=qty_var,
            width=5,
            font=("Arial", 11)
        )
        qty_entry.pack(side=LEFT, padx=(5, 0))

        # Botón agregar
        btn_add = ttk.Button(
            controls_row,
            text="+ Agregar",
            command=lambda: self.add_to_order(product_id, name, price_var, qty_var),
            bootstyle="success-outline"
        )
        btn_add.pack(side=RIGHT)

        # Guardar referencias
        self.product_widgets[product_id] = {
            'price_var': price_var,
            'qty_var': qty_var,
            'default_price': default_price
        }

    def add_to_order(self, product_id, name, price_var, qty_var):
        """Agregar producto al pedido"""
        try:
            price = float(price_var.get())
            quantity = float(qty_var.get())

            if price <= 0 or quantity <= 0:
                mb.showwarning("Error", "El precio y cantidad deben ser mayores a 0")
                return

            # Buscar si ya existe en el pedido
            for item in self.order_items:
                if item['id'] == product_id and item['price'] == price:
                    item['quantity'] += quantity
                    item['subtotal'] = item['quantity'] * item['price']
                    self.refresh_order_summary()
                    return

            # Agregar nuevo item
            self.order_items.append({
                'id': product_id,
                'name': name,
                'price': price,
                'quantity': quantity,
                'subtotal': price * quantity
            })

            self.refresh_order_summary()

            # Reset cantidad a 1
            qty_var.set("1")

        except ValueError:
            mb.showwarning("Error", "Ingrese valores numéricos válidos")

    def refresh_order_summary(self):
        """Actualizar el resumen del pedido"""
        # Limpiar items actuales
        for widget in self.items_inner_frame.winfo_children():
            widget.destroy()

        if not self.order_items:
            self.no_items_label = ttk.Label(
                self.items_inner_frame,
                text="Sin productos",
                font=("Arial", 10),
                bootstyle="secondary"
            )
            self.no_items_label.pack(pady=20)
            self.total_label.config(text="$0.00")
            self.update_save_button_state()
            return

        # Mostrar items
        for i, item in enumerate(self.order_items):
            self.create_order_item_card(i, item)

        # Calcular y mostrar total
        total = sum(item['subtotal'] for item in self.order_items)
        self.total_label.config(text=f"${total:.2f}")

        self.update_save_button_state()

    def create_order_item_card(self, index, item):
        """Crear tarjeta de item en el resumen"""
        card = ttk.Frame(self.items_inner_frame, bootstyle="light")
        card.pack(fill=X, pady=2, padx=2)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=8, pady=6)

        # Info del producto
        info_frame = ttk.Frame(content)
        info_frame.pack(fill=X)

        ttk.Label(
            info_frame,
            text=item['name'],
            font=("Arial", 10, "bold")
        ).pack(side=LEFT)

        ttk.Label(
            info_frame,
            text=f"x{item['quantity']:.0f}",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        # Precio y subtotal
        price_frame = ttk.Frame(content)
        price_frame.pack(fill=X)

        ttk.Label(
            price_frame,
            text=f"${item['price']:.2f} c/u",
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=LEFT)

        ttk.Label(
            price_frame,
            text=f"${item['subtotal']:.2f}",
            font=("Arial", 10, "bold"),
            bootstyle="success"
        ).pack(side=RIGHT)

        # Botón eliminar
        btn_delete = ttk.Button(
            content,
            text="Eliminar",
            command=lambda: self.remove_from_order(index),
            bootstyle="danger-link",
            width=8
        )
        btn_delete.pack(anchor=E, pady=(4, 0))

    def remove_from_order(self, index):
        """Eliminar item del pedido"""
        if 0 <= index < len(self.order_items):
            del self.order_items[index]
            self.refresh_order_summary()

    def update_save_button_state(self):
        """Habilitar/deshabilitar botón de guardar"""
        if self.selected_customer and self.order_items:
            self.btn_save_order.config(state=NORMAL)
        else:
            self.btn_save_order.config(state=DISABLED)

    def save_order(self):
        """Guardar el pedido"""
        if not self.selected_customer:
            mb.showwarning("Error", "Seleccione un cliente")
            return

        if not self.order_items:
            mb.showwarning("Error", "Agregue productos al pedido")
            return

        total = sum(item['subtotal'] for item in self.order_items)

        success, result = order_provider.save(
            items=self.order_items,
            total=total,
            customer_id=self.selected_customer.id
        )

        if success:
            mb.showinfo(
                "Pedido Guardado",
                f"Pedido #{result} guardado correctamente\n\n"
                f"Cliente: {self.selected_customer.customer_name}\n"
                f"Total: ${total:.2f}"
            )
            self.clear_order()
        else:
            mb.showerror("Error", f"Error al guardar pedido:\n{result}")

    def clear_order(self):
        """Limpiar el pedido actual"""
        self.order_items = []
        self.selected_customer = None

        # Reset UI
        self.selected_customer_label.config(
            text="Ninguno seleccionado",
            bootstyle="secondary"
        )
        self.products_frame.config(text="  Productos - Seleccione un cliente  ")
        self.products_content_frame.pack_forget()
        self.no_customer_label.pack(expand=YES)

        self.refresh_order_summary()
        self.display_customers()

    def filter_customers(self, *args):
        """Filtrar clientes por búsqueda"""
        self.display_customers(self.customer_search_var.get())

    # Mouse wheel handlers for customers
    def _on_mousewheel_customers(self, event):
        if event.num == 4 or event.delta > 0:
            self.customers_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.customers_canvas.yview_scroll(1, "units")

    def _bind_mousewheel_customers(self):
        self.customers_canvas.bind_all("<MouseWheel>", self._on_mousewheel_customers)
        self.customers_canvas.bind_all("<Button-4>", self._on_mousewheel_customers)
        self.customers_canvas.bind_all("<Button-5>", self._on_mousewheel_customers)

    def _unbind_mousewheel_customers(self):
        self.customers_canvas.unbind_all("<MouseWheel>")
        self.customers_canvas.unbind_all("<Button-4>")
        self.customers_canvas.unbind_all("<Button-5>")

    # Mouse wheel handlers for products
    def _on_mousewheel_products(self, event):
        if event.num == 4 or event.delta > 0:
            self.products_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.products_canvas.yview_scroll(1, "units")

    def _bind_mousewheel_products(self):
        self.products_canvas.bind_all("<MouseWheel>", self._on_mousewheel_products)
        self.products_canvas.bind_all("<Button-4>", self._on_mousewheel_products)
        self.products_canvas.bind_all("<Button-5>", self._on_mousewheel_products)

    def _unbind_mousewheel_products(self):
        self.products_canvas.unbind_all("<MouseWheel>")
        self.products_canvas.unbind_all("<Button-4>")
        self.products_canvas.unbind_all("<Button-5>")
