import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from app.data.providers.sales import sale_provider
from app.data.providers.customers import customer_provider
from app.data.database import get_db
from app.models import Customer
from datetime import datetime, timedelta


class SalesList(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content
        self.sales_list = []
        self.customers_cache = {}
        self.customers_list = []
        self.selected_customer_filter = None

        self.setup_ui()
        self.load_sales()

    def setup_ui(self):
        """Configurar la interfaz"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(
            header_frame,
            text="Ventas",
            font=("Arial", 20, "bold")
        ).pack(side=LEFT)

        btn_refresh = ttk.Button(
            header_frame,
            text="Actualizar",
            command=self.load_sales,
            bootstyle="info-outline"
        )
        btn_refresh.pack(side=RIGHT)

        # Filtros - Fila 1: Fecha
        date_filter_frame = ttk.Frame(self)
        date_filter_frame.pack(fill=X, padx=10, pady=(0, 5))

        ttk.Label(date_filter_frame, text="Filtrar por fecha:").pack(side=LEFT)

        self.date_start = DateEntry(
            date_filter_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y",
            startdate=datetime.now() - timedelta(days=30)
        )
        self.date_start.pack(side=LEFT, padx=(5, 0))

        ttk.Label(date_filter_frame, text="hasta").pack(side=LEFT, padx=5)

        self.date_end = DateEntry(
            date_filter_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y"
        )
        self.date_end.pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            date_filter_frame,
            text="Filtrar",
            command=self.filter_sales_by_date,
            bootstyle="info-outline"
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            date_filter_frame,
            text="Limpiar",
            command=self.clear_date_filter,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)

        # Filtros - Fila 2: Cliente
        customer_filter_frame = ttk.Frame(self)
        customer_filter_frame.pack(fill=X, padx=10, pady=(0, 10))

        ttk.Label(customer_filter_frame, text="Filtrar por cliente:").pack(side=LEFT)

        self.customer_search_var = ttk.StringVar()
        self.customer_search_var.trace_add('write', self.on_customer_search_change)

        self.customer_search_entry = ttk.Entry(
            customer_filter_frame,
            textvariable=self.customer_search_var,
            width=25
        )
        self.customer_search_entry.pack(side=LEFT, padx=(5, 0))

        self.customer_filter_label = ttk.Label(
            customer_filter_frame,
            text="Todos los clientes",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.customer_filter_label.pack(side=LEFT, padx=(10, 0))

        self.btn_clear_customer = ttk.Button(
            customer_filter_frame,
            text="X",
            command=self.clear_customer_filter,
            bootstyle="danger-outline",
            width=3
        )
        self.btn_clear_customer.pack(side=LEFT, padx=(5, 0))
        self.btn_clear_customer.pack_forget()

        self.customer_dropdown = None
        self.customer_listbox = None

        # Container principal con dos paneles
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        # Panel izquierdo: Lista de ventas
        self.list_frame = ttk.Labelframe(main_container, text="  Lista de Ventas  ", padding=10)
        self.list_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

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

        # Panel derecho: Detalles de la venta
        self.detail_frame = ttk.Labelframe(main_container, text="  Detalles de la Venta  ", padding=10, width=350)
        self.detail_frame.pack(side=LEFT, fill=Y)
        self.detail_frame.pack_propagate(False)

        self.detail_content = ttk.Frame(self.detail_frame)
        self.detail_content.pack(fill=BOTH, expand=YES)

        self.no_selection_label = ttk.Label(
            self.detail_content,
            text="Selecciona una venta\npara ver sus detalles",
            font=("Arial", 12),
            bootstyle="secondary",
            justify=CENTER
        )
        self.no_selection_label.pack(expand=YES)

    def load_sales(self):
        """Cargar todas las ventas"""
        self.sales_list = sale_provider.get_all()
        self.load_customers_cache()
        self.display_sales()

    def load_customers_cache(self):
        """Cargar nombres de clientes en cache (incluye Mostrador)"""
        db = get_db()
        try:
            all_customers = db.query(Customer.id, Customer.customer_name).filter(
                Customer.active == True
            ).all()
            self.customers_cache = {c.id: c.customer_name for c in all_customers}
        finally:
            db.close()

        # Para el dropdown de busqueda, usar solo clientes visibles
        self.customers_list = customer_provider.get_all()

    def filter_sales_by_date(self):
        """Filtrar ventas por rango de fechas"""
        start = self.date_start.entry.get()
        end = self.date_end.entry.get()

        try:
            start_date = datetime.strptime(start, "%d/%m/%Y").date()
            end_date = datetime.strptime(end, "%d/%m/%Y").date()
        except ValueError:
            return

        self.sales_list = sale_provider.get_by_date_range(start_date, end_date)
        self.display_sales()

    def clear_date_filter(self):
        """Limpiar filtro de fechas"""
        self.date_start.entry.delete(0, 'end')
        self.date_end.entry.delete(0, 'end')

        now = datetime.now()
        self.date_start.entry.insert(0, (now - timedelta(days=30)).strftime("%d/%m/%Y"))
        self.date_end.entry.insert(0, now.strftime("%d/%m/%Y"))

        self.sales_list = sale_provider.get_all()
        self.display_sales()

    def display_sales(self):
        """Mostrar lista de ventas"""
        for widget in self.list_inner_frame.winfo_children():
            widget.destroy()

        filtered = self.sales_list

        # Filtrar por cliente
        if self.selected_customer_filter:
            filtered = [s for s in filtered if s.customer_id == self.selected_customer_filter]

        if not filtered:
            ttk.Label(
                self.list_inner_frame,
                text="No hay ventas",
                font=("Arial", 12),
                bootstyle="secondary"
            ).pack(pady=40)
            return

        for sale in filtered:
            self.create_sale_card(sale)

    def create_sale_card(self, sale):
        """Crear tarjeta de venta"""
        card = ttk.Frame(
            self.list_inner_frame,
            bootstyle="info",
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
            text=f"Venta #{sale.id}",
            font=("Arial", 13, "bold")
        ).pack(side=LEFT)

        date_str = sale.date.strftime("%d/%m/%Y %H:%M") if sale.date else "N/A"
        ttk.Label(
            top_row,
            text=date_str,
            font=("Arial", 9),
            bootstyle="secondary"
        ).pack(side=RIGHT)

        # Fila media: Cliente
        customer_name = self.customers_cache.get(sale.customer_id, "Cliente desconocido")
        ttk.Label(
            content,
            text=f"Cliente: {customer_name}",
            font=("Arial", 10)
        ).pack(anchor=W, pady=(5, 0))

        # Fila inferior: Total
        bottom_row = ttk.Frame(content)
        bottom_row.pack(fill=X, pady=(8, 0))

        ttk.Label(
            bottom_row,
            text=f"${sale.total:.2f}",
            font=("Arial", 14, "bold"),
            bootstyle="success"
        ).pack(side=LEFT)

        # Hacer clickeable
        for widget in [card, content]:
            widget.bind("<Button-1>", lambda e, s=sale: self.show_sale_details(s))
            widget.configure(cursor="hand2")

    def show_sale_details(self, sale):
        """Mostrar detalles de una venta"""
        for widget in self.detail_content.winfo_children():
            widget.destroy()

        sale_data = sale_provider.get_by_id(sale.id)

        if not sale_data:
            ttk.Label(
                self.detail_content,
                text="Error al cargar detalles",
                bootstyle="danger"
            ).pack(pady=20)
            return

        # Header con ID
        ttk.Label(
            self.detail_content,
            text=f"Venta #{sale_data['id']}",
            font=("Arial", 16, "bold")
        ).pack(anchor=W)

        # Fecha
        date_str = sale_data['date'].strftime("%d/%m/%Y %H:%M") if sale_data['date'] else "N/A"
        ttk.Label(
            self.detail_content,
            text=date_str,
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(anchor=W)

        ttk.Separator(self.detail_content).pack(fill=X, pady=10)

        # Cliente
        customer_name = self.customers_cache.get(sale_data['customer_id'], "Cliente desconocido")
        client_frame = ttk.Frame(self.detail_content)
        client_frame.pack(fill=X)

        ttk.Label(client_frame, text="Cliente:", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(client_frame, text=customer_name, font=("Arial", 10)).pack(side=LEFT, padx=(5, 0))

        ttk.Separator(self.detail_content).pack(fill=X, pady=10)

        # Productos
        ttk.Label(
            self.detail_content,
            text="Productos:",
            font=("Arial", 11, "bold")
        ).pack(anchor=W)

        products_frame = ttk.Frame(self.detail_content)
        products_frame.pack(fill=BOTH, expand=YES, pady=(5, 10))

        for detail in sale_data['details']:
            item_frame = ttk.Frame(products_frame, bootstyle="light")
            item_frame.pack(fill=X, pady=2)

            item_content = ttk.Frame(item_frame)
            item_content.pack(fill=X, padx=8, pady=6)

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
            text=f"${sale_data['total']:.2f}",
            font=("Arial", 16, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=RIGHT, padx=10, pady=8)

    # --- Filtro de cliente (mismo patron que OrdersList) ---

    def on_customer_search_change(self, *args):
        """Manejar cambios en el campo de busqueda de cliente"""
        search_text = self.customer_search_var.get().lower()

        if not search_text:
            self.hide_customer_dropdown()
            return

        filtered = [
            c for c in self.customers_list
            if search_text in (c.customer_name or '').lower()
        ]

        self.show_customer_dropdown(filtered)

    def show_customer_dropdown(self, customers):
        """Mostrar dropdown con resultados de busqueda"""
        self.hide_customer_dropdown()

        if not customers:
            return

        self.customer_dropdown = ttk.Toplevel(self)
        self.customer_dropdown.overrideredirect(True)
        self.customer_dropdown.attributes('-topmost', True)

        self.customer_search_entry.update_idletasks()
        x = self.customer_search_entry.winfo_rootx()
        y = self.customer_search_entry.winfo_rooty() + self.customer_search_entry.winfo_height()
        width = self.customer_search_entry.winfo_width()

        self.customer_dropdown.geometry(f"{width}x{min(5, len(customers)) * 25 + 10}+{x}+{y}")

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
        self.customer_dropdown.bind("<FocusOut>", lambda e: self.hide_customer_dropdown())

    def hide_customer_dropdown(self):
        """Ocultar dropdown de clientes"""
        if self.customer_dropdown:
            self.customer_dropdown.destroy()
            self.customer_dropdown = None
            self.customer_listbox = None

    def on_customer_select(self, event):
        """Manejar seleccion de cliente para filtrar"""
        if not self.customer_listbox:
            return

        selection = self.customer_listbox.selection()
        if not selection:
            return

        item = self.customer_listbox.item(selection[0])
        customer_id = int(item['tags'][0])
        customer_name = item['text']

        self.selected_customer_filter = customer_id

        self.customer_filter_label.config(
            text=f"Cliente: {customer_name}",
            bootstyle="info"
        )
        self.btn_clear_customer.pack(side=LEFT, padx=(5, 0))

        self.customer_search_var.set("")
        self.hide_customer_dropdown()

        self.display_sales()

    def clear_customer_filter(self):
        """Limpiar filtro de cliente"""
        self.selected_customer_filter = None
        self.customer_filter_label.config(
            text="Todos los clientes",
            bootstyle="secondary"
        )
        self.btn_clear_customer.pack_forget()
        self.customer_search_var.set("")
        self.display_sales()

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
