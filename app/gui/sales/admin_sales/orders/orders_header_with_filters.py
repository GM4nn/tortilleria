import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.providers.customers import customer_provider
from app.constants import ORDER_STATUSES


class OrdersHeaderWithFilters(ttk.Frame):
    def __init__(self, parent, on_refresh, on_filter):
        super().__init__(parent)
        self.on_refresh = on_refresh
        self.on_filter = on_filter
        self.customers_list = []
        self.selected_customer_filter = None
        self.customer_dropdown = None
        self.customer_listbox = None

        self.setup_ui()

    def setup_ui(self):
        self.setup_header()
        self.setup_status_filter()
        self.setup_customer_filter()

    def setup_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(
            header_frame,
            text="Pedidos",
            font=("Arial", 20, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            header_frame,
            text="Actualizar",
            command=self.on_refresh,
            bootstyle="info-outline"
        ).pack(side=RIGHT)

    def setup_status_filter(self):
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=X, padx=10, pady=(0, 5))

        ttk.Label(filter_frame, text="Filtrar por estado:").pack(side=LEFT)

        self.status_var = ttk.StringVar(value="")
        statuses = [(info["label"], key) for key, info in ORDER_STATUSES.items()]

        for text, value in statuses:
            ttk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.status_var,
                value=value,
                command=self.on_filter,
                bootstyle="info-toolbutton"
            ).pack(side=LEFT, padx=5)

    def setup_customer_filter(self):
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

    def load_customers(self):
        self.customers_list = customer_provider.get_all()

    def get_status_filter(self):
        return self.status_var.get()

    def get_customer_filter(self):
        return self.selected_customer_filter

    # --- Filtro de cliente ---

    def on_customer_search_change(self, *args):
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
        if self.customer_dropdown:
            self.customer_dropdown.destroy()
            self.customer_dropdown = None
            self.customer_listbox = None

    def on_customer_select(self, event):
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

        self.on_filter()

    def clear_customer_filter(self):
        self.selected_customer_filter = None
        self.customer_filter_label.config(
            text="Todos los clientes",
            bootstyle="secondary"
        )
        self.btn_clear_customer.pack_forget()
        self.customer_search_var.set("")
        self.on_filter()
