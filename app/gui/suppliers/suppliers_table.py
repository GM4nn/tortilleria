import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.data.providers.suppliers import supplier_provider


class SuppliersTable(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = supplier_provider
        self.main_container = main_container

        self.setup_ui()
        self.load_suppliers()


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
            text="Gestión de Proveedores",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT)

        search_frame = ttk.Frame(header)
        search_frame.pack(side=RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_suppliers())

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=RIGHT)


    def setup_table_section(self):

        columns = [
            {"text": "ID", "stretch": False, "width": 50},
            {"text": "Empresa", "stretch": True},
            {"text": "Contacto", "stretch": True},
            {"text": "Teléfono", "stretch": False, "width": 120},
            {"text": "Tipo Producto", "stretch": False, "width": 120},
            {"text": "Ciudad", "stretch": False, "width": 100}
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

        self.table.view.bind('<<TreeviewSelect>>', self.on_supplier_select)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Refrescar",
            command=self.load_suppliers,
            bootstyle="info-outline",
            width=15
        ).pack(side=LEFT)


    def filter_suppliers(self):

        search_term = self.search_var.get().lower()

        if not search_term:
            self.display_suppliers(self.all_suppliers)
            return

        filtered = [
            s for s in self.all_suppliers
            if search_term in s['name'].lower() or
               search_term in str(s['id']) or
               search_term in (s['contact_name'] or '').lower() or
               search_term in (s['phone'] or '').lower() or
               search_term in (s['product_type'] or '').lower() or
               search_term in (s['city'] or '').lower()
        ]

        self.display_suppliers(filtered)


    def on_supplier_select(self, _event):

        selection = self.table.view.selection()
        if not selection:
            return

        item = self.table.view.item(selection[0])
        values = item['values']

        if not values:
            return

        supplier_id = values[0]

        supplier = next((s for s in self.all_suppliers if s['id'] == supplier_id), None)

        if supplier and hasattr(self.parent, 'form_section'):
            form = self.parent.form_section
            form.selected_supplier_id = supplier_id
            form.id_label.config(text=str(supplier_id))
            form.name_var.set(supplier['name'])
            form.contact_var.set(supplier['contact_name'] or '')
            form.phone_var.set(supplier['phone'] or '')
            form.email_var.set(supplier['email'] or '')
            form.address_var.set(supplier['address'] or '')
            form.city_var.set(supplier['city'] or '')
            form.product_type_var.set(supplier['product_type'] or '')
            form.notes_text.delete('1.0', 'end')
            form.notes_text.insert('1.0', supplier['notes'] or '')


    def clear_selection(self):

        for item in self.table.view.selection():
            self.table.view.selection_remove(item)


    def display_suppliers(self, suppliers):

        self.table.delete_rows()

        rows = []
        for supplier in suppliers:
            rows.append([
                supplier['id'],
                supplier['name'],
                supplier['contact_name'] or 'N/A',
                supplier['phone'] or 'N/A',
                supplier['product_type'] or 'General',
                supplier['city'] or 'N/A'
            ])

        if rows:
            self.table.insert_rows(0, rows)

        self.table.load_table_data()


    def load_suppliers(self):

        suppliers = self.provider.get_all()
        self.all_suppliers = []

        for (supplier_id, name, contact_name, phone, email, address,
             city, product_type, notes, created_at, updated_at) in suppliers:
            self.all_suppliers.append({
                'id': supplier_id,
                'name': name,
                'contact_name': contact_name,
                'phone': phone,
                'email': email,
                'address': address,
                'city': city,
                'product_type': product_type,
                'notes': notes,
                'created_at': created_at,
                'updated_at': updated_at
            })

        self.display_suppliers(self.all_suppliers)
