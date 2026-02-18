import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.widgets import DateEntry
from app.data.providers.sales import sale_provider
from app.gui.components.server_paginated_table import ServerPaginatedTableview
from app.gui.sales.admin_sales.sales.sale_detail import SaleDetail
from datetime import timedelta, datetime
from app.constants import mexico_now


class SalesList(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content
        self.all_sales = []

        self.setup_ui()

    def setup_ui(self):

        self.setup_header()
        self.setup_date_filter()

        # Main container: table (left) + detail (right)
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        self.setup_table(main_container)
        self.setup_detail_panel(main_container)

    def setup_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(
            header_frame,
            text="Ventas",
            font=("Arial", 20, "bold")
        ).pack(side=LEFT)

        ttk.Button(
            header_frame,
            text="Actualizar",
            command=self.load_sales,
            bootstyle="info-outline"
        ).pack(side=RIGHT)

    def setup_date_filter(self):
        date_filter_frame = ttk.Frame(self)
        date_filter_frame.pack(fill=X, padx=10, pady=(0, 5))

        ttk.Label(date_filter_frame, text="Filtrar por fecha:").pack(side=LEFT)

        self.date_start = DateEntry(
            date_filter_frame,
            bootstyle="info",
            dateformat="%d/%m/%Y",
            startdate=mexico_now() - timedelta(days=30)
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

    def setup_table(self, parent):
        columns = [
            {"text": "# Venta",  "stretch": False, "width": 80},
            {"text": "Fecha",    "stretch": True},
            {"text": "Total",    "stretch": False, "width": 150},
        ]

        table_frame = ttk.Frame(parent)
        table_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        self.table = ServerPaginatedTableview(
            master=table_frame,
            coldata=columns,
            fetch_page=self._fetch_sales_page,
            count_rows=sale_provider.get_count,
            pagesize=40,
            bootstyle=PRIMARY,
        )

        self.table.pack(fill=BOTH, expand=YES)

        self.table.view.bind('<<TreeviewSelect>>', self.on_sale_select)

    def setup_detail_panel(self, parent):
        self.detail_panel = SaleDetail(parent)
        self.detail_panel.pack(side=RIGHT, fill=BOTH, expand=YES)

    def _fetch_sales_page(self, offset, limit):
        sales = sale_provider.get_all(offset, limit)
        rows = []
        for sale in sales:
            date_str = sale.date.strftime("%d/%m/%Y %H:%M") if sale.date else "N/A"
            rows.append([sale.id, date_str, f"${sale.total:.2f}"])
        return rows

    def on_sale_select(self, _event):

        selection = self.table.view.selection()
        if not selection:
            return

        item = self.table.view.item(selection[0])
        values = item['values']

        if not values:
            return

        sale_id = values[0]
        self.detail_panel.show_sale(sale_id)

    def load_sales(self):
        self.table.refresh()

    def filter_sales_by_date(self):
        start = self.date_start.entry.get()
        end = self.date_end.entry.get()

        try:
            start_date = datetime.strptime(start, "%d/%m/%Y").date()
            end_date = datetime.strptime(end, "%d/%m/%Y").date()
        except ValueError:
            return

        sales = sale_provider.get_by_date_range(start_date, end_date)
        filtered = []

        for sale in sales:
            date_str = sale.date.strftime("%d/%m/%Y %H:%M") if sale.date else "N/A"
            filtered.append({
                'id': sale.id,
                'date': date_str,
                'total': f"${sale.total:.2f}"
            })

        self.all_sales = filtered
        self.display_sales(self.all_sales)

    def clear_date_filter(self):

        self.date_start.entry.delete(0, 'end')
        self.date_end.entry.delete(0, 'end')

        now = mexico_now()
        self.date_start.entry.insert(0, (now - timedelta(days=30)).strftime("%d/%m/%Y"))
        self.date_end.entry.insert(0, now.strftime("%d/%m/%Y"))

        self.load_sales()
