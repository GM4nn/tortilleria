import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.data.providers.sales import sale_provider


class SaleDetail(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="  Detalle de Venta  ", padding=10)

        self.setup_ui()

    def setup_ui(self):
        
        self.setup_gui_header()
        self.setup_gui_table_products()
        self.setup_gui_total()

    def setup_gui_header(self):

        info_frame = ttk.Frame(self)
        info_frame.pack(fill=X, pady=(0, 10))

        self.sale_id_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 14, "bold")
        )
        self.sale_id_label.pack(anchor=W)

        self.sale_date_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 10),
            bootstyle="secondary"
        )
        self.sale_date_label.pack(anchor=W)

        ttk.Separator(self).pack(fill=X, pady=(0, 10))

    def setup_gui_table_products(self):
        columns = [
            {"text": "Producto",     "stretch": True},
            {"text": "Cantidad",     "stretch": False, "width": 80},
            {"text": "P. Unitario",  "stretch": False, "width": 100},
            {"text": "Subtotal",     "stretch": False, "width": 100},
        ]

        self.products_table = Tableview(
            master=self,
            coldata=columns,
            rowdata=[],
            paginated=False,
            searchable=False,
            bootstyle=PRIMARY,
            height=10
        )
        self.products_table.pack(fill=BOTH, expand=YES)

        # Mensaje inicial
        self.no_selection_label = ttk.Label(
            self,
            text="Selecciona una venta\npara ver sus productos",
            font=("Arial", 12),
            bootstyle="secondary",
            justify=CENTER
        )
        self.no_selection_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def setup_gui_total(self):
        
        total_frame = ttk.Frame(self, bootstyle="dark")
        total_frame.pack(fill=X, pady=(10, 0))

        ttk.Label(
            total_frame,
            text="TOTAL:",
            font=("Arial", 12, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=LEFT, padx=10, pady=8)

        self.total_label = ttk.Label(
            total_frame,
            text="$0.00",
            font=("Arial", 14, "bold"),
            bootstyle="inverse-dark"
        )
        self.total_label.pack(side=RIGHT, padx=10, pady=8)

    def show_sale(self, sale_id):

        sale_data = sale_provider.get_by_id(sale_id)

        if not sale_data:
            return

        # Hide initial message
        self.no_selection_label.place_forget()

        # Sale information
        date_str = sale_data['date'].strftime("%d/%m/%Y %H:%M") if sale_data['date'] else "N/A"
        self.sale_id_label.config(text=f"Venta #{sale_data['id']}")
        self.sale_date_label.config(text=date_str)

        # Total
        self.total_label.config(text=f"${sale_data['total']:.2f}")

        # Products
        self.products_table.delete_rows()

        rows = []
        for detail in sale_data['details']:
            rows.append([
                detail['product_name'],
                f"{detail['quantity']:.0f}",
                f"${detail['unit_price']:.2f}",
                f"${detail['subtotal']:.2f}"
            ])

        if rows:
            self.products_table.insert_rows(0, rows)

        self.products_table.load_table_data()
