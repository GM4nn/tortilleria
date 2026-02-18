from math import ceil
from ttkbootstrap.tableview import Tableview, TableRow


class ServerPaginatedTableview(Tableview):
    """
    Tableview con paginacion server-side (OFFSET/LIMIT).

    Parametros extra:
        fetch_page: callable(offset, limit) -> list[list]
        count_rows: callable() -> int
    """

    def __init__(self, master, coldata, fetch_page, count_rows,
                 pagesize=10, **kwargs):
        self._fetch_page = fetch_page
        self._count_rows = count_rows
        self._server_total = 0
        self._loading = False
        self._initialized = False

        kwargs.pop('autoalign', None)
        kwargs.pop('autofit', None)
        super().__init__(
            master=master,
            coldata=coldata,
            rowdata=[],
            paginated=True,
            pagesize=pagesize,
            autoalign=False,
            autofit=False,
            **kwargs
        )

        # Diferir primera carga hasta que tkinter termine de construir todo
        self.after_idle(self._first_load)

    def _first_load(self):
        self._initialized = True
        self._rowindex.set(0)
        self._load_server_page()

    def _load_server_page(self):
        if self._loading or not self._initialized:
            return
        self._loading = True

        try:
            offset = max(0, self._rowindex.get())
            limit = self._pagesize.get()
            self._server_total = self._count_rows()
            total_pages = ceil(self._server_total / limit) if self._server_total > 0 else 1

            rows = self._fetch_page(offset, limit)

            # Limpiar vista y datos internos
            self.unload_table_data()
            for row in self._tablerows:
                if row.iid:
                    try:
                        self.view.delete(row.iid)
                    except Exception:
                        pass
            self._tablerows.clear()
            self._viewdata.clear()
            self._iidmap.clear()

            # Crear y mostrar filas directamente
            for i, values in enumerate(rows):
                record = TableRow(self, values)
                self._tablerows.append(record)
                stripe = self._stripecolor is not None and i % 2 == 0
                record.show(stripe)
                self._viewdata.append(record)

            # Setear paginacion
            self._pagelimit.set(total_pages)
            pageindex = (offset // limit) + 1 if self._server_total > 0 else 1
            self._pageindex.set(min(total_pages, pageindex))

        finally:
            self._loading = False

    # ─── Override paginacion ──────────────────────────────────

    def goto_first_page(self):
        if not self._initialized:
            return
        self._rowindex.set(0)
        self._load_server_page()

    def goto_last_page(self):
        if not self._initialized:
            return
        total = self._count_rows()
        limit = self._pagesize.get()
        last_page = max(ceil(total / limit) - 1, 0)
        self._rowindex.set(self.pagesize * last_page)
        self._load_server_page()

    def goto_next_page(self):
        if not self._initialized:
            return
        if self._pageindex.get() >= self._pagelimit.get():
            return
        self._rowindex.set(self._rowindex.get() + self.pagesize)
        self._load_server_page()

    def goto_prev_page(self):
        if not self._initialized:
            return
        if self._pageindex.get() <= 1:
            return
        self._rowindex.set(self._rowindex.get() - self.pagesize)
        self._load_server_page()

    def goto_page(self, *_):
        if not self._initialized:
            return
        pagelimit = self._pagelimit.get()
        pageindex = self._pageindex.get()
        if pageindex > pagelimit:
            pageindex = pagelimit
            self._pageindex.set(pageindex)
        elif pageindex <= 0:
            pageindex = 1
            self._pageindex.set(pageindex)
        self._rowindex.set((pageindex * self.pagesize) - self.pagesize)
        self._load_server_page()

    # ─── Override sort (el orden viene del SQL) ───────────────

    def sort_column_data(self, event=None, cid=None, sort=None):
        pass

    def refresh(self):
        self._rowindex.set(0)
        self._load_server_page()
