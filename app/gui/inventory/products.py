import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview


class ProductsInventory(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.db = self.app.db
        self.main_container = main_container

        self.setup_ui()
        self.load_products()
    

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
            text="Inventario de Productos",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT)

        search_frame = ttk.Frame(header)
        search_frame.pack(side=RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_products())

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=RIGHT)


    def setup_table_section(self):

        columns = [
            {"text": "ID", "stretch": False, "width": 60},
            {"text": "Nombre del Producto", "stretch": True},
            {"text": "Precio", "stretch": False, "width": 100},
            {"text": "Estado", "stretch": False, "width": 100}
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

        self.table.view.bind('<<TreeviewSelect>>', self.on_product_select)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Refrescar",
            command=self.load_products,
            bootstyle="info-outline",
            width=15
        ).pack(side=LEFT)


    def filter_products(self):

        search_term = self.search_var.get().lower()

        if not search_term:
            self.display_products(self.all_products)
            return

        filtered = [
            p for p in self.all_products
            if search_term in p['name'].lower() or
               search_term in str(p['id']) or
               search_term in f"{p['price']:.2f}"
        ]

        self.display_products(filtered)


    def on_product_select(self, _event):

        selection = self.table.view.selection()
        if not selection:
            return

        item = self.table.view.item(selection[0])
        values = item['values']

        if not values:
            return

        product_id = values[0]
        product_name = values[1]
        product_price = values[2].replace('$', '')

        if hasattr(self.parent, 'form_section'):
            form = self.parent.form_section
            form.selected_product_id = product_id
            form.id_label.config(text=str(product_id))
            form.name_var.set(product_name)
            form.price_var.set(product_price)


    def clear_selection(self):

        for item in self.table.view.selection():
            self.table.view.selection_remove(item)


    def display_products(self, products):

        self.table.delete_rows()

        rows = []
        for product in products:
            estado = "Activo" if product.get('active', 1) == 1 else "Inactivo"
            rows.append([
                product['id'],
                product['name'],
                f"${product['price']:.2f}",
                estado
            ])

        if rows:
            self.table.insert_rows(0, rows)

        self.table.load_table_data()


    def load_products(self):

        products = self.db.get_products()
        self.all_products = []

        for product_id, name, price in products:
            self.all_products.append({
                'id': product_id,
                'name': name,
                'price': price,
                'active': 1
            })

        self.display_products(self.all_products)
