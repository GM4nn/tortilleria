import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from datetime import datetime, timedelta
from app.data.providers.customers import customer_provider
from app.constants import ORDER_STATUSES, ORDER_STATUSES_ALL, PAYMENT_STATUSES, PAYMENT_STATUS_ALL, mexico_now


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
        self.setup_filters()

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

    def setup_filters(self):
        filters_frame = ttk.Frame(self)
        filters_frame.pack(fill=X, padx=10, pady=(0, 10))
        filters_frame.columnconfigure(1, weight=1)

        label_width = 25

        # --- Fila 0: Fecha ---
        today = mexico_now()
        start_of_week = today - timedelta(days=today.weekday())

        ttk.Label(
            filters_frame,
            text="Fecha:",
            width=label_width,
            anchor=W
        ).grid(row=0, column=0, sticky=W, pady=3)

        date_frame = ttk.Frame(filters_frame)
        date_frame.grid(row=0, column=1, sticky=W, pady=3)

        self.date_start = DateEntry(
            date_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y",
            startdate=start_of_week
        )
        self.date_start.pack(side=LEFT)

        ttk.Label(date_frame, text="hasta").pack(side=LEFT, padx=5)

        self.date_end = DateEntry(
            date_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y"
        )
        self.date_end.pack(side=LEFT)

        ttk.Button(
            date_frame,
            text="Filtrar",
            command=self.on_filter,
            bootstyle="info-outline"
        ).pack(side=LEFT, padx=(10, 5))

        ttk.Button(
            date_frame,
            text="Limpiar",
            command=self.clear_date_filter,
            bootstyle="secondary-outline"
        ).pack(side=LEFT)

        # --- Fila 1: Estado de entrega ---
        ttk.Label(
            filters_frame,
            text="Estado de entrega:",
            width=label_width,
            anchor=W
        ).grid(row=1, column=0, sticky=W, pady=3)

        status_btns_frame = ttk.Frame(filters_frame)
        status_btns_frame.grid(row=1, column=1, sticky=W, pady=3)

        self.status_var = ttk.StringVar(value=ORDER_STATUSES_ALL)
        for key, info in ORDER_STATUSES.items():
            ttk.Radiobutton(
                status_btns_frame,
                text=info["label"],
                variable=self.status_var,
                value=key,
                command=self.on_filter,
                bootstyle=f"{info['color']}-toolbutton"
            ).pack(side=LEFT, padx=(0, 5))

        # --- Fila 2: Estado de pago ---
        ttk.Label(
            filters_frame,
            text="Estado de pago:",
            width=label_width,
            anchor=W
        ).grid(row=2, column=0, sticky=W, pady=3)

        payment_btns_frame = ttk.Frame(filters_frame)
        payment_btns_frame.grid(row=2, column=1, sticky=W, pady=3)

        self.payment_status_var = ttk.StringVar(value=PAYMENT_STATUS_ALL)
        for key, info in PAYMENT_STATUSES.items():
            ttk.Radiobutton(
                payment_btns_frame,
                text=info["label"],
                variable=self.payment_status_var,
                value=key,
                command=self.on_filter,
                bootstyle=f"{info['color']}-toolbutton"
            ).pack(side=LEFT, padx=(0, 5))

        # --- Fila 3: Cliente ---
        ttk.Label(
            filters_frame,
            text="Cliente:",
            width=label_width,
            anchor=W
        ).grid(row=3, column=0, sticky=W, pady=3)

        customer_frame = ttk.Frame(filters_frame)
        customer_frame.grid(row=3, column=1, sticky=W, pady=3)

        self.customer_search_var = ttk.StringVar()
        self.customer_search_var.trace_add('write', self.on_customer_search_change)

        self.customer_search_entry = ttk.Entry(
            customer_frame,
            textvariable=self.customer_search_var,
            width=25
        )
        self.customer_search_entry.pack(side=LEFT)

        self.customer_filter_label = ttk.Label(
            customer_frame,
            text="Todos los clientes",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.customer_filter_label.pack(side=LEFT, padx=(10, 0))

        self.btn_clear_customer = ttk.Button(
            customer_frame,
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

    def get_payment_status_filter(self):
        return self.payment_status_var.get()

    def get_date_filter(self):
        start = self.date_start.entry.get()
        end = self.date_end.entry.get()
        try:
            start_date = datetime.strptime(start, "%d/%m/%Y").date()
            end_date = datetime.strptime(end, "%d/%m/%Y").date()
            return start_date, end_date
        except ValueError:
            return None

    def clear_date_filter(self):
        self.date_start.entry.delete(0, "end")
        self.date_end.entry.delete(0, "end")
        self.on_filter()

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
