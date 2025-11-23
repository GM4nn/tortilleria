import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.data.providers.supplies import supply_provider


class SuppliesTable(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = supply_provider
        self.main_container = main_container

        self.setup_ui()
        self.load_supplies()


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
            text="Gestión de Insumos",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT)

        search_frame = ttk.Frame(header)
        search_frame.pack(side=RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_supplies())

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=25
        )
        search_entry.pack(side=RIGHT)


    def setup_table_section(self):

        columns = [
            {"text": "ID", "stretch": False, "width": 50},
            {"text": "Insumo", "stretch": False, "width": 120},
            {"text": "Proveedor", "stretch": False, "width": 120},
            {"text": "Cantidad", "stretch": False, "width": 80},
            {"text": "Unidad", "stretch": False, "width": 70},
            {"text": "P. Unidad", "stretch": True, "width": 90},
            {"text": "Total", "stretch": True, "width": 100},
            {"text": "Fecha", "stretch": False, "width": 90}
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

        self.table.view.bind('<<TreeviewSelect>>', self.on_supply_select)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Refrescar",
            command=self.load_supplies,
            bootstyle="info-outline",
            width=15
        ).pack(side=LEFT)


    def filter_supplies(self):

        search_term = self.search_var.get().lower()

        if not search_term:
            self.display_supplies(self.all_supplies)
            return

        filtered = [
            s for s in self.all_supplies
            if search_term in s['supply_name'].lower() or
               search_term in str(s['id']) or
               search_term in s['supplier_name'].lower() or
               search_term in s['unit'].lower()
        ]

        self.display_supplies(filtered)


    def on_supply_select(self, _event):

        selection = self.table.view.selection()
        if not selection:
            return

        item = self.table.view.item(selection[0])
        values = item['values']

        if not values:
            return

        supply_id = values[0]

        supply = next((s for s in self.all_supplies if s['id'] == supply_id), None)

        if supply and hasattr(self.parent, 'form_section'):
            form = self.parent.form_section
            form.load_supply(supply)


    def clear_selection(self):

        for item in self.table.view.selection():
            self.table.view.selection_remove(item)


    def display_supplies(self, supplies):

        self.table.delete_rows()

        rows = []
        for supply in supplies:
            date_str = supply['purchase_date'].strftime("%d/%m/%Y") if supply['purchase_date'] else ''
            rows.append([
                supply['id'],
                supply['supply_name'],
                supply['supplier_name'],
                f"{supply['quantity']:.2f}",
                supply['unit'],
                f"${supply['unit_price']:.2f}",
                f"${supply['total_price']:.2f}",
                date_str
            ])

        if rows:
            self.table.insert_rows(0, rows)

        self.table.load_table_data()


    def load_supplies(self):

        supplies = self.provider.get_all()
        self.all_supplies = supplies

        self.display_supplies(self.all_supplies)
