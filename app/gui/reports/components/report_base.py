"""
BaseReportTab - Clase base para todos los tabs de reportes.
Provee: scrollable frame, refresh_data, helpers para KPIs, tablas y cards.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.database import SessionLocal


class BaseReportTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        self.canvas = ttk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def refresh_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        with SessionLocal() as db:
            self.build_sections(db)

    def build_sections(self, db):
        raise NotImplementedError

    def add_separator(self):
        ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

    def create_section(self, parent, title, subtitle, bootstyle="primary"):
        section = ttk.Labelframe(parent, text=title, padding=20, bootstyle=bootstyle)
        section.pack(fill=X, padx=20, pady=10)

        if subtitle:
            ttk.Label(
                section, text=subtitle,
                font=("Segoe UI", 10), foreground="#6c757d"
            ).pack(anchor=W, pady=(0, 15))

        return section

    def create_kpi_cards(self, parent, kpis):
        """
        kpis: list of dicts {title, value, color, bootstyle}
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=X, padx=20, pady=10)

        for i, kpi in enumerate(kpis):
            card = ttk.Labelframe(frame, text=kpi["title"], padding=10, bootstyle=kpi.get("bootstyle", "light"))
            padx = (0, 10) if i < len(kpis) - 1 else (0, 0)
            if i > 0:
                padx = (10, 10) if i < len(kpis) - 1 else (10, 0)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=padx)

            ttk.Label(
                card, text=str(kpi["value"]),
                font=("Segoe UI", 18, "bold"),
                foreground=kpi.get("color", "#212529")
            ).pack(pady=(5, 5))

        return frame

    def create_table(self, parent, headers, rows, money_cols=None):
        """
        headers: list of (text, width)
        rows: list of lists of values
        money_cols: set of column indices that should be formatted as money
        """
        money_cols = money_cols or set()

        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 5))
        for text, width in headers:
            ttk.Label(
                header_frame, text=text,
                font=("Segoe UI", 10, "bold"), width=width
            ).pack(side=LEFT, padx=5)

        # Rows
        for row in rows:
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=X, pady=2)

            for col_idx, (value, (_, width)) in enumerate(zip(row, headers)):
                kwargs = {"width": width}
                if col_idx in money_cols:
                    kwargs["foreground"] = "#28a745"
                    kwargs["font"] = ("Segoe UI", 10, "bold")

                ttk.Label(row_frame, text=str(value), **kwargs).pack(side=LEFT, padx=5)

        return len(rows) > 0

    def create_highlight_cards(self, parent, best, worst):
        """
        best/worst: dict {title, name, details: [(label, value)], color}
        """
        cards_frame = ttk.Frame(parent)
        cards_frame.pack(fill=X, pady=(20, 0))

        for i, data in enumerate([best, worst]):
            if data is None:
                continue

            bootstyle = "success" if i == 0 else "danger"
            color = data.get("color", "#28a745" if i == 0 else "#dc3545")

            card = ttk.Labelframe(
                cards_frame, text=data["title"],
                padding=15, bootstyle=bootstyle
            )
            padx = (0, 10) if i == 0 else (10, 0)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=padx)

            ttk.Label(
                card, text=data["name"],
                font=("Segoe UI", 14, "bold"), foreground=color
            ).pack(anchor=W)

            for label, value in data.get("details", []):
                ttk.Label(
                    card, text=f"{label}: {value}",
                    font=("Segoe UI", 10)
                ).pack(anchor=W, pady=(3, 0))

        return cards_frame

    def create_empty_state(self, parent, message):
        ttk.Label(
            parent, text=message,
            foreground="#6c757d", font=("Segoe UI", 10, "italic")
        ).pack(pady=10)
