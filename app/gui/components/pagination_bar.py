from math import ceil
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class PaginationBar(ttk.Frame):
    """
    Barra de paginacion reutilizable que replica el estilo del Tableview.

    Parametros:
        on_page_change: callable() que se invoca al cambiar de pagina.
        pagesize: cantidad de items por pagina (default 10).
    """

    def __init__(self, master, on_page_change, pagesize=10, **kwargs):
        super().__init__(master, **kwargs)
        self._on_page_change = on_page_change
        self._pagesize = pagesize
        self._total_items = 0
        self._pageindex = tk.IntVar(value=1)
        self._pagelimit = tk.IntVar(value=1)

        self._build_ui()

    def _build_ui(self):
        ttk.Button(
            self, text="»",
            command=self.goto_last_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)

        ttk.Button(
            self, text="›",
            command=self.goto_next_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)

        ttk.Button(
            self, text="‹",
            command=self.goto_prev_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)

        ttk.Button(
            self, text="«",
            command=self.goto_first_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)

        ttk.Separator(self, orient=VERTICAL).pack(side=RIGHT, padx=10)

        ttk.Label(self, textvariable=self._pagelimit).pack(side=RIGHT, padx=(0, 5))
        ttk.Label(self, text="de").pack(side=RIGHT, padx=(5, 0))

        index = ttk.Entry(self, textvariable=self._pageindex, width=4)
        index.pack(side=RIGHT)
        index.bind("<Return>", lambda e: self.goto_page(), "+")
        index.bind("<KP_Enter>", lambda e: self.goto_page(), "+")

        ttk.Label(self, text="Pagina").pack(side=RIGHT, padx=5)

    # --- API publica ---

    def update_total(self, total_items):
        self._total_items = total_items
        total_pages = ceil(total_items / self._pagesize) if total_items > 0 else 1
        self._pagelimit.set(total_pages)
        if self._pageindex.get() > total_pages:
            self._pageindex.set(total_pages)

    def get_offset(self):
        return (self._pageindex.get() - 1) * self._pagesize

    def reset(self):
        self._pageindex.set(1)

    # --- Navegacion ---

    def goto_first_page(self):
        self._pageindex.set(1)
        self._on_page_change()

    def goto_last_page(self):
        self._pageindex.set(self._pagelimit.get())
        self._on_page_change()

    def goto_next_page(self):
        if self._pageindex.get() >= self._pagelimit.get():
            return
        self._pageindex.set(self._pageindex.get() + 1)
        self._on_page_change()

    def goto_prev_page(self):
        if self._pageindex.get() <= 1:
            return
        self._pageindex.set(self._pageindex.get() - 1)
        self._on_page_change()

    def goto_page(self):
        page = self._pageindex.get()
        limit = self._pagelimit.get()
        if page > limit:
            self._pageindex.set(limit)
        elif page <= 0:
            self._pageindex.set(1)
        self._on_page_change()
