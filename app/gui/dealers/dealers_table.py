import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.data.providers.dealers import dealer_provider


class DealersTable(ttk.Frame):
    def __init__(self, parent, app, main_container):
        super().__init__(parent)
        self.app = app
        self.parent = parent
        self.provider = dealer_provider
        self.main_container = main_container
        self.all_dealers = []

        self.setup_ui()
        self.load_dealers()

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
            text="Gestión de Repartidores",
            font=("Arial", 18, "bold")
        ).pack(side=LEFT)

        search_frame = ttk.Frame(header)
        search_frame.pack(side=RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_dealers())

        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side=RIGHT)

    def setup_table_section(self):

        columns = [
            {"text": "ID", "stretch": False, "width": 50},
            {"text": "Nombre", "stretch": True},
            {"text": "Usuario", "stretch": True},
            {"text": "PIN", "stretch": False, "width": 100},
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

        self.table.view.bind('<<TreeviewSelect>>', self.on_dealer_select)

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame, text="Refrescar", command=self.load_dealers,
            bootstyle="info-outline", width=15
        ).pack(side=LEFT)

    def filter_dealers(self):

        term = self.search_var.get().lower()

        if not term:
            self.display_dealers(self.all_dealers)
            return

        filtered = [
            d for d in self.all_dealers
            if term in d['name'].lower()
            or term in d['username'].lower()
            or term in str(d['id'])
        ]

        self.display_dealers(filtered)

    def on_dealer_select(self, _event):

        selection = self.table.view.selection()
        if not selection:
            return

        values = self.table.view.item(selection[0])['values']
        if not values:
            return

        dealer_id = values[0]
        dealer = next((d for d in self.all_dealers if d['id'] == dealer_id), None)

        if dealer and hasattr(self.parent, 'form_section'):
            form = self.parent.form_section
            form.selected_dealer_id = dealer_id
            form.id_label.config(text=str(dealer_id))
            form.name_var.set(dealer['name'])
            form.username_var.set(dealer['username'])
            form.pin_var.set(dealer['pin'])

    def clear_selection(self):
        for item in self.table.view.selection():
            self.table.view.selection_remove(item)

    def display_dealers(self, dealers):

        self.table.delete_rows()

        rows = [[d['id'], d['name'], d['username'], d['pin']] for d in dealers]

        if rows:
            self.table.insert_rows(0, rows)

        self.table.load_table_data()

    def load_dealers(self):

        dealers = self.provider.get_all()
        self.all_dealers = [
            {'id': dealer_id, 'username': username, 'pin': pin, 'name': name}
            for (dealer_id, username, pin, name) in dealers
        ]
        self.display_dealers(self.all_dealers)
