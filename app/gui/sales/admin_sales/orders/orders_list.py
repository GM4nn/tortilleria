import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.data.providers.orders import order_provider
from app.data.providers.customers import customer_provider


class OrdersList(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content
        self.orders_list = []
        self.customers_cache = {}  # Cache de nombres de clientes
        self.customers_list = []  # Lista completa de clientes
        self.selected_customer_filter = None  # Cliente seleccionado para filtrar

        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        """Configurar la interfaz"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(
            header_frame,
            text="Pedidos",
            font=("Arial", 20, "bold")
        ).pack(side=LEFT)

        # Botón refrescar
        btn_refresh = ttk.Button(
            header_frame,
            text="Actualizar",
            command=self.load_orders,
            bootstyle="info-outline"
        )
        btn_refresh.pack(side=RIGHT)

        # Filtros - Fila 1: Estado
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=X, padx=10, pady=(0, 5))

        ttk.Label(filter_frame, text="Filtrar por estado:").pack(side=LEFT)

        self.status_var = ttk.StringVar(value="todos")
        statuses = [("Todos", "todos"), ("Pendientes", "pendiente"), ("Completados", "completado"), ("Cancelados", "cancelado")]

        for text, value in statuses:
            ttk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.status_var,
                value=value,
                command=self.filter_orders,
                bootstyle="info-toolbutton"
            ).pack(side=LEFT, padx=5)

        # Filtros - Fila 2: Cliente
        customer_filter_frame = ttk.Frame(self)
        customer_filter_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttk.Label(customer_filter_frame, text="Filtrar por cliente:").pack(side=LEFT)

        # Entry de búsqueda
        self.customer_search_var = ttk.StringVar()
        self.customer_search_var.trace_add('write', self.on_customer_search_change)

        self.customer_search_entry = ttk.Entry(
            customer_filter_frame,
            textvariable=self.customer_search_var,
            width=25
        )
        self.customer_search_entry.pack(side=LEFT, padx=(5, 0))

        # Label de cliente seleccionado
        self.customer_filter_label = ttk.Label(
            customer_filter_frame,
            text="Todos los clientes",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.customer_filter_label.pack(side=LEFT, padx=(10, 0))

        # Botón limpiar filtro de cliente
        self.btn_clear_customer = ttk.Button(
            customer_filter_frame,
            text="X",
            command=self.clear_customer_filter,
            bootstyle="danger-outline",
            width=3
        )
        self.btn_clear_customer.pack(side=LEFT, padx=(5, 0))
        self.btn_clear_customer.pack_forget()  # Ocultar inicialmente

        # Toplevel para dropdown de resultados (se crea cuando se necesita)
        self.customer_dropdown = None
        self.customer_listbox = None

        # Container principal con dos paneles
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        # Panel izquierdo: Lista de pedidos
        self.list_frame = ttk.Labelframe(main_container, text="  Lista de Pedidos  ", padding=10)
        self.list_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Canvas para lista con scroll
        list_canvas_frame = ttk.Frame(self.list_frame)
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

        # Panel derecho: Detalles del pedido
        self.detail_frame = ttk.Labelframe(main_container, text="  Detalles del Pedido  ", padding=10, width=350)
        self.detail_frame.pack(side=LEFT, fill=Y)
        self.detail_frame.pack_propagate(False)

        self.detail_content = ttk.Frame(self.detail_frame)
        self.detail_content.pack(fill=BOTH, expand=YES)

        # Mensaje inicial
        self.no_selection_label = ttk.Label(
            self.detail_content,
            text="Selecciona un pedido\npara ver sus detalles",
            font=("Arial", 12),
            bootstyle="secondary",
            justify=CENTER
        )
        self.no_selection_label.pack(expand=YES)

    def load_orders(self):
        """Cargar todos los pedidos"""
        self.orders_list = order_provider.get_all()
        self.load_customers_cache()
        self.display_orders()

    def load_customers_cache(self):
        """Cargar nombres de clientes en cache"""
        self.customers_list = customer_provider.get_all()
        self.customers_cache = {c.id: c.customer_name for c in self.customers_list}

    def filter_orders(self):
        """Filtrar pedidos por estado"""
        self.display_orders()

    def display_orders(self):
        """Mostrar lista de pedidos"""
        # Limpiar lista actual
        for widget in self.list_inner_frame.winfo_children():
            widget.destroy()

        status_filter = self.status_var.get()

        filtered = self.orders_list

        # Filtrar por estado
        if status_filter != "todos":
            filtered = [o for o in filtered if o.status == status_filter]

        # Filtrar por cliente
        if self.selected_customer_filter:
            filtered = [o for o in filtered if o.customer_id == self.selected_customer_filter]

        if not filtered:
            ttk.Label(
                self.list_inner_frame,
                text="No hay pedidos",
                font=("Arial", 12),
                bootstyle="secondary"
            ).pack(pady=40)
            return

        for order in filtered:
            self.create_order_card(order)

    def create_order_card(self, order):
        """Crear tarjeta de pedido"""
        # Determinar estilo según estado
        if order.status == "pendiente":
            border_style = "warning"
        elif order.status == "completado":
            border_style = "success"
        else:
            border_style = "secondary"

        card = ttk.Frame(
            self.list_inner_frame,
            bootstyle=border_style,
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

        # Formatear fecha
        date_str = order.date.strftime("%d/%m/%Y %H:%M") if order.date else "N/A"
        ttk.Label(
            top_row,
            text=date_str,
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        # Fila media: Cliente
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

        # Badge de estado
        status_colors = {
            "pendiente": "warning",
            "completado": "success",
            "cancelado": "secondary"
        }
        status_text = {
            "pendiente": "Pendiente",
            "completado": "Completado",
            "cancelado": "Cancelado"
        }

        status_badge = ttk.Label(
            bottom_row,
            text=f"  {status_text.get(order.status, order.status)}  ",
            font=("Arial", 9, "bold"),
            bootstyle=f"inverse-{status_colors.get(order.status, 'secondary')}"
        )
        status_badge.pack(side=RIGHT)

        # Hacer clickeable
        for widget in [card, content]:
            widget.bind("<Button-1>", lambda e, o=order: self.show_order_details(o))
            widget.configure(cursor="hand2")

    def show_order_details(self, order):
        """Mostrar detalles de un pedido"""
        # Limpiar contenido anterior
        for widget in self.detail_content.winfo_children():
            widget.destroy()

        # Obtener detalles completos
        order_data = order_provider.get_by_id(order.id)

        if not order_data:
            ttk.Label(
                self.detail_content,
                text="Error al cargar detalles",
                bootstyle="danger"
            ).pack(pady=20)
            return

        # Header con ID
        ttk.Label(
            self.detail_content,
            text=f"Pedido #{order_data['id']}",
            font=("Arial", 16, "bold")
        ).pack(anchor=W)

        # Fecha
        date_str = order_data['date'].strftime("%d/%m/%Y %H:%M") if order_data['date'] else "N/A"
        ttk.Label(
            self.detail_content,
            text=date_str,
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Separator(self.detail_content).pack(fill=X, pady=10)

        # Cliente
        customer_name = self.customers_cache.get(order_data['customer_id'], "Cliente desconocido")
        client_frame = ttk.Frame(self.detail_content)
        client_frame.pack(fill=X)

        ttk.Label(client_frame, text="Cliente:", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(client_frame, text=customer_name, font=("Arial", 10)).pack(side=LEFT, padx=(5, 0))

        # Estado
        status_frame = ttk.Frame(self.detail_content)
        status_frame.pack(fill=X, pady=(5, 0))

        ttk.Label(status_frame, text="Estado:", font=("Arial", 10, "bold")).pack(side=LEFT)

        status_colors = {"pendiente": "warning", "completado": "success", "cancelado": "secondary"}
        status_text = {"pendiente": "Pendiente", "completado": "Completado", "cancelado": "Cancelado"}

        ttk.Label(
            status_frame,
            text=f"  {status_text.get(order_data['status'], order_data['status'])}  ",
            font=("Arial", 9, "bold"),
            bootstyle=f"inverse-{status_colors.get(order_data['status'], 'secondary')}"
        ).pack(side=LEFT, padx=(5, 0))

        ttk.Separator(self.detail_content).pack(fill=X, pady=10)

        # Productos
        ttk.Label(
            self.detail_content,
            text="Productos:",
            font=("Arial", 11, "bold")
        ).pack(anchor=W)

        products_frame = ttk.Frame(self.detail_content)
        products_frame.pack(fill=BOTH, expand=YES, pady=(5, 10))

        for detail in order_data['details']:
            item_frame = ttk.Frame(products_frame, bootstyle="light")
            item_frame.pack(fill=X, pady=2)

            item_content = ttk.Frame(item_frame)
            item_content.pack(fill=X, padx=8, pady=6)

            # Nombre y cantidad
            ttk.Label(
                item_content,
                text=f"{detail['product_name']}",
                font=("Arial", 10, "bold")
            ).pack(anchor=W)

            detail_row = ttk.Frame(item_content)
            detail_row.pack(fill=X)

            ttk.Label(
                detail_row,
                text=f"x{detail['quantity']:.0f} @ ${detail['unit_price']:.2f}",
                font=("Arial", 9),
                bootstyle="secondary"
            ).pack(side=LEFT)

            ttk.Label(
                detail_row,
                text=f"${detail['subtotal']:.2f}",
                font=("Arial", 10, "bold"),
                bootstyle="success"
            ).pack(side=RIGHT)

        # Total
        total_frame = ttk.Frame(self.detail_content, bootstyle="dark")
        total_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            total_frame,
            text="TOTAL:",
            font=("Arial", 12, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=LEFT, padx=10, pady=8)

        ttk.Label(
            total_frame,
            text=f"${order_data['total']:.2f}",
            font=("Arial", 16, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=RIGHT, padx=10, pady=8)

        # Botones de acción (solo si está pendiente)
        if order_data['status'] == 'pendiente':
            btn_frame = ttk.Frame(self.detail_content)
            btn_frame.pack(fill=X)

            ttk.Button(
                btn_frame,
                text="Marcar Completado",
                command=lambda: self.update_order_status(order_data['id'], 'completado'),
                bootstyle="success"
            ).pack(fill=X, pady=2)

            ttk.Button(
                btn_frame,
                text="Cancelar Pedido",
                command=lambda: self.update_order_status(order_data['id'], 'cancelado'),
                bootstyle="danger-outline"
            ).pack(fill=X, pady=2)

    def update_order_status(self, order_id, new_status):
        """Actualizar estado del pedido"""
        status_text = {"completado": "completar", "cancelado": "cancelar"}

        if not mb.askyesno("Confirmar", f"¿Desea {status_text.get(new_status, new_status)} este pedido?"):
            return

        success, result = order_provider.update_status(order_id, new_status)

        if success:
            mb.showinfo("Éxito", f"Pedido #{order_id} actualizado")
            self.load_orders()

            # Limpiar panel de detalles
            for widget in self.detail_content.winfo_children():
                widget.destroy()
            self.no_selection_label = ttk.Label(
                self.detail_content,
                text="Selecciona un pedido\npara ver sus detalles",
                font=("Arial", 12),
                bootstyle="secondary",
                justify=CENTER
            )
            self.no_selection_label.pack(expand=YES)
        else:
            mb.showerror("Error", f"Error al actualizar: {result}")

    def on_customer_search_change(self, *args):
        """Manejar cambios en el campo de búsqueda de cliente"""
        search_text = self.customer_search_var.get().lower()

        if not search_text:
            self.hide_customer_dropdown()
            return

        # Filtrar clientes
        filtered = [
            c for c in self.customers_list
            if search_text in (c.customer_name or '').lower()
        ]

        self.show_customer_dropdown(filtered)

    def show_customer_dropdown(self, customers):
        """Mostrar dropdown con resultados de búsqueda"""
        self.hide_customer_dropdown()

        if not customers:
            return

        # Crear ventana Toplevel para el dropdown
        self.customer_dropdown = ttk.Toplevel(self)
        self.customer_dropdown.overrideredirect(True)  # Sin barra de título
        self.customer_dropdown.attributes('-topmost', True)  # Siempre encima

        # Posicionar debajo del entry de búsqueda
        self.customer_search_entry.update_idletasks()
        x = self.customer_search_entry.winfo_rootx()
        y = self.customer_search_entry.winfo_rooty() + self.customer_search_entry.winfo_height()
        width = self.customer_search_entry.winfo_width()

        self.customer_dropdown.geometry(f"{width}x{min(5, len(customers)) * 25 + 10}+{x}+{y}")

        # Crear listbox con resultados
        self.customer_listbox = ttk.Treeview(
            self.customer_dropdown,
            columns=(),
            show="tree",
            height=min(5, len(customers))
        )
        self.customer_listbox.pack(fill=BOTH, expand=YES)
        self.customer_listbox.column("#0", width=0, stretch=True)

        for customer in customers:
            self.customer_listbox.insert(
                "",
                "end",
                text=customer.customer_name,
                tags=(str(customer.id),)
            )

        self.customer_listbox.bind("<<TreeviewSelect>>", self.on_customer_select)

        # Cerrar dropdown si se hace click fuera
        self.customer_dropdown.bind("<FocusOut>", lambda e: self.hide_customer_dropdown())

    def hide_customer_dropdown(self):
        """Ocultar dropdown de clientes"""
        if self.customer_dropdown:
            self.customer_dropdown.destroy()
            self.customer_dropdown = None
            self.customer_listbox = None

    def on_customer_select(self, event):
        """Manejar selección de cliente para filtrar"""
        if not self.customer_listbox:
            return

        selection = self.customer_listbox.selection()
        if not selection:
            return

        item = self.customer_listbox.item(selection[0])
        customer_id = int(item['tags'][0])
        customer_name = item['text']

        # Guardar filtro
        self.selected_customer_filter = customer_id

        # Actualizar UI
        self.customer_filter_label.config(
            text=f"Cliente: {customer_name}",
            bootstyle="info"
        )
        self.btn_clear_customer.pack(side=LEFT, padx=(5, 0))

        # Limpiar búsqueda y ocultar dropdown
        self.customer_search_var.set("")
        self.hide_customer_dropdown()

        # Aplicar filtro
        self.display_orders()

    def clear_customer_filter(self):
        """Limpiar filtro de cliente"""
        self.selected_customer_filter = None
        self.customer_filter_label.config(
            text="Todos los clientes",
            bootstyle="secondary"
        )
        self.btn_clear_customer.pack_forget()
        self.customer_search_var.set("")
        self.display_orders()

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
