import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.data.providers.cash_cut import cash_cut_provider


class HistoryPanel(ttk.Labelframe):
    def __init__(self, parent, content):
        super().__init__(parent, text="Historial de Cortes", padding=10)
        self.content = content
        self.provider = cash_cut_provider

        self.page = 0
        self.page_size = 8
        self.total_rows = 0

        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        # Table
        columns = [
            {"text": "#", "stretch": False, "width": 50},
            {"text": "Fecha Cierre", "stretch": True, "width": 160},
            {"text": "Ventas", "stretch": False, "width": 70},
            {"text": "Pedidos", "stretch": False, "width": 70},
            {"text": "Esperado", "stretch": True, "width": 120},
            {"text": "Declarado", "stretch": True, "width": 120},
            {"text": "Diferencia", "stretch": True, "width": 120},
        ]

        self.table = Tableview(
            self,
            coldata=columns,
            rowdata=[],
            paginated=False,
            searchable=False,
            autofit=True,
            height=6,
        )
        self.table.pack(fill=BOTH, expand=YES)

        # Pagination controls
        nav = ttk.Frame(self)
        nav.pack(fill=X, pady=(10, 0))

        self.btn_prev = ttk.Button(
            nav, text="Anterior", command=self._prev_page, bootstyle="outline", width=10,
        )
        self.btn_prev.pack(side=LEFT)

        self.lbl_page = ttk.Label(nav, text="", font=("Segoe UI", 10))
        self.lbl_page.pack(side=LEFT, expand=YES)

        self.btn_next = ttk.Button(
            nav, text="Siguiente", command=self._next_page, bootstyle="outline", width=10,
        )
        self.btn_next.pack(side=RIGHT)

    def refresh(self):
        self.total_rows = self.provider.get_count()
        self._load_page()

    def _load_page(self):
        offset = self.page * self.page_size
        rows = self.provider.get_all(offset=offset, limit=self.page_size)

        table_data = []
        for row in rows:
            cut_id, closed_at, expected, declared, diff, s_count, o_count = row
            date_str = closed_at.strftime("%d/%b/%Y %H:%M") if closed_at else "---"

            # Format difference with sign
            if abs(diff) < 0.01:
                diff_str = "$0.00"
            elif diff > 0:
                diff_str = f"+${diff:,.2f}"
            else:
                diff_str = f"-${abs(diff):,.2f}"

            table_data.append((
                cut_id,
                date_str,
                s_count,
                o_count,
                f"${expected:,.2f}",
                f"${declared:,.2f}",
                diff_str,
            ))

        self.table.delete_rows()
        if table_data:
            self.table.insert_rows(END, table_data)
        self.table.load_table_data()

        # Update pagination
        total_pages = max(1, (self.total_rows + self.page_size - 1) // self.page_size)
        current = self.page + 1
        self.lbl_page.config(text=f"Pagina {current} de {total_pages}")
        self.btn_prev.config(state=NORMAL if self.page > 0 else DISABLED)
        self.btn_next.config(state=NORMAL if current < total_pages else DISABLED)

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self._load_page()

    def _next_page(self):
        total_pages = max(1, (self.total_rows + self.page_size - 1) // self.page_size)
        if self.page + 1 < total_pages:
            self.page += 1
            self._load_page()
