import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.data.providers.customers import customer_provider


class CustomersTable(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = customer_provider
        self.main_container = main_container

        self.setup_ui()
        self.load_customers()


    def setup_ui(self):

        self.left_frame = ttk.Frame(self.main_container)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.setup_header()
        self.setup_table_section()


    def setup_header(self):

        header = ttk.Frame(self.left_frame)
        header.pack(fill=X, pady=(0, 10))

        ttk.Label(
            header,
            text="Gestión de Clientes",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT)

        search_frame = ttk.Frame(header)
        search_frame.pack(side=RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_customers())

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=RIGHT)


    def setup_table_section(self):

        columns = [
            {"text": "ID", "stretch": False, "width": 60},
            {"text": "Nombre", "stretch": True},
            {"text": "Teléfono", "stretch": False, "width": 120},
            {"text": "Categoría", "stretch": False, "width": 120},
            {"text": "Dirección", "stretch": True}
        ]

        table_frame = ttk.Frame(self.left_frame)
        table_frame.pack(fill=BOTH, expand=YES)

        self.table = Tableview(
            master=table_frame,
            coldata=columns,
            rowdata=[],
            paginated=True,
            searchable=False,
            bootstyle=PRIMARY,
            pagesize=15,
            height=20
        )
        self.table.pack(fill=BOTH, expand=YES)

        self.table.view.bind('<<TreeviewSelect>>', self.on_customer_select)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Refrescar",
            command=self.load_customers,
            bootstyle="info-outline",
            width=15
        ).pack(side=LEFT)


    def filter_customers(self):

        search_term = self.search_var.get().lower()

        if not search_term:
            self.display_customers(self.all_customers)
            return

        filtered = [
            c for c in self.all_customers
            if search_term in c['name'].lower() or
               search_term in str(c['id']) or
               search_term in (c['phone'] or '').lower() or
               search_term in (c['category'] or '').lower() or
               search_term in (c['direction'] or '').lower()
        ]

        self.display_customers(filtered)


    def on_customer_select(self, _event):

        selection = self.table.view.selection()
        if not selection:
            return

        item = self.table.view.item(selection[0])
        values = item['values']

        if not values:
            return

        customer_id = values[0]

        customer = next((c for c in self.all_customers if c['id'] == customer_id), None)

        if customer and hasattr(self.parent, 'form_section'):
            form = self.parent.form_section
            form.selected_customer_id = customer_id
            form.id_label.config(text=str(customer_id))
            form.name_var.set(customer['name'])
            form.phone_var.set(customer['phone'] or '')
            form.direction_var.set(customer['direction'] or '')
            form.category_var.set(customer['category'])
            form.photo_var.set(customer['photo'] or '')

            if customer['photo']:
                form.update_image_preview(customer['photo'])
            else:
                form.update_image_preview(None)

    def clear_selection(self):

        for item in self.table.view.selection():
            self.table.view.selection_remove(item)


    def display_customers(self, customers):

        self.table.delete_rows()

        rows = []
        for customer in customers:
            rows.append([
                customer['id'],
                customer['name'],
                customer['phone'] or 'N/A',
                customer['category'] or 'General',
                customer['direction'] or 'N/A'
            ])

        if rows:
            self.table.insert_rows(0, rows)

        self.table.load_table_data()


    def load_customers(self):

        customers = self.provider.get_all()
        self.all_customers = []

        for customer_id, name, direction, category, photo, phone, created_at, updated_at in customers:
            self.all_customers.append({
                'id': customer_id,
                'name': name,
                'direction': direction,
                'category': category,
                'photo': photo,
                'phone': phone,
                'created_at': created_at,
                'updated_at': updated_at
            })

        self.display_customers(self.all_customers)
