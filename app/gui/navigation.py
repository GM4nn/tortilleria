from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import tkinter as tk

from app.gui.ai_assistant.content import AIAssistantContent
from app.gui.suppliers.content import SuppliersContent
from app.gui.customers.content import CustomersContent
from app.gui.inventory.content import InventoryContent
from app.gui.supplies.content import SuppliesContent
from app.gui.reports.content import ReportsContent
from app.gui.sales.pos.content import SalesContent
from app.gui.sales.admin_sales.sales_admin_content import SalesAdminContent


class Navigation(tk.Frame):
    # Colors
    BG = "#353C40"
    FG = "#ffffff"
    FG_MUTED = "#95a5a6"
    ACCENT = "#3498db"
    SEP = "#34495e"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg=self.BG, width=230)
        self.pack_propagate(False)

        self.expanded = {}
        self.menu_data = {}

        self._build_ui()

    def _frame(self, parent):
        f = tk.Frame(parent)
        f.configure(background=self.BG)
        
        return f

    def _label(self, parent, text, font_size=10, bold=False, fg=None):
        """Create label with correct background color and text"""
        font = ("Segoe UI", font_size, "bold") if bold else ("Segoe UI", font_size)
        color = fg if fg else self.FG
        l = tk.Label(parent, text=text, font=font, anchor="w")
        l.configure(background=self.BG, foreground=color)
        return l

    def _build_ui(self):
        self._build_header()
        sep = tk.Frame(self, height=1)
        sep.configure(background=self.SEP)
        sep.pack(fill=X, padx=15, pady=(0, 10))
        self._build_menu()

    def _build_header(self):
        header = self._frame(self)
        header.pack(pady=(20, 15), padx=15, fill=X)

        try:
            logo_image = Image.open("tortilleria_logo.png")
            logo_image = logo_image.resize((45, 45), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_image)
            logo_lbl = tk.Label(header, image=self.logo)
            logo_lbl.configure(background=self.BG)
            logo_lbl.pack(side=LEFT, padx=(0, 10))
        except:
            logo_lbl = self._label(header, "🌽", 24, fg=self.ACCENT)
            logo_lbl.pack(side=LEFT, padx=(0, 10))

        title_box = self._frame(header)
        title_box.pack(side=LEFT)
        self._label(title_box, "Tierra del Campo", 12, bold=True).pack(anchor="w")
        self._label(title_box, "Sistema POS", 9, fg=self.FG_MUTED).pack(anchor="w")

    def _build_menu(self):
        menu = self._frame(self)
        menu.pack(fill=BOTH, expand=True, padx=10)

        items = [
            ("🛒", "Ventas", "sales_menu", True, [
                ("Punto de Venta", "sales", True),
                ("Administrar Ventas", "sales_admin", True)
            ]),
            ("📦", "Productos", "products_menu", True, [
                ("Inventario", "inventory", True),
                ("Categorías", "categories", False)
            ]),
            ("💵", "Caja", "cash", False, None),
            ("📥", "Compras", "purchases_menu", True, [
                ("Proveedores", "suppliers", True),
                ("Insumos", "supplies", True)
            ]),
            ("📈", "Reportes", "reports", True, None),
            None,
            ("⚙️", "Configuración", "config", False, None),
            ("👥", "Clientes", "customers", True, None),
            ("🤖", "Asistente IA", "ai_assistant", True, None)
        ]

        for item in items:
            if item is None:
                sep = tk.Frame(menu, height=1)
                sep.configure(background=self.SEP)
                sep.pack(fill=X, pady=8, padx=5)
            else:
                self._add_item(menu, *item)

    def _add_item(self, parent, icon, text, view, enabled, children):
        item_box = self._frame(parent)
        item_box.pack(fill=X, pady=2)

        row = self._frame(item_box)
        row.pack(fill=X)

        # Indicator
        indicator = tk.Frame(row, width=4)
        indicator.configure(background=self.BG)
        indicator.pack(side=LEFT, fill=Y)

        # Icon
        fg = self.FG if enabled else self.FG_MUTED
        icon_lbl = self._label(row, icon, 11, fg=fg)
        icon_lbl.pack(side=LEFT, padx=(8, 10), pady=8)

        # Text
        text_lbl = self._label(row, text, 10, fg=fg)
        text_lbl.pack(side=LEFT, fill=X, expand=True, pady=8)

        # Arrow
        arrow_lbl = None
        if children:
            arrow_lbl = self._label(row, "‹", 12, fg=self.FG_MUTED)
            arrow_lbl.pack(side=RIGHT, padx=(0, 12))
            self.expanded[view] = False

        self.menu_data[view] = {
            "indicator": indicator,
            "arrow": arrow_lbl,
            "children": children,
            "child_frame": None,
            "child_data": []
        }

        # Children
        if children:
            child_frame = self._frame(item_box)
            self.menu_data[view]["child_frame"] = child_frame
            for c_text, c_view, c_enabled in children:
                self._add_child(child_frame, c_text, c_view, c_enabled, view)

        # Click event
        if enabled:
            widgets = [row, icon_lbl, text_lbl]
            if arrow_lbl:
                widgets.append(arrow_lbl)
            for w in widgets:
                w.config(cursor="hand2")
                if children:
                    w.bind("<Button-1>", lambda e, v=view: self._toggle(v))
                else:
                    w.bind("<Button-1>", lambda e, v=view: self.change_view(v))

    def _add_child(self, parent, text, view, enabled, parent_view):
        row = self._frame(parent)
        row.pack(fill=X)

        indicator = tk.Frame(row, width=4)
        indicator.configure(background=self.BG)
        indicator.pack(side=LEFT, fill=Y)

        fg = self.FG_MUTED if enabled else "#555"
        circle = self._label(row, "○", 9, fg=fg)
        circle.pack(side=LEFT, padx=(35, 8), pady=6)

        fg2 = self.FG if enabled else self.FG_MUTED
        text_lbl = self._label(row, text, 10, fg=fg2)
        text_lbl.pack(side=LEFT, fill=X, expand=True, pady=6)

        self.menu_data[parent_view]["child_data"].append({
            "indicator": indicator,
            "circle": circle,
            "view": view,
            "enabled": enabled
        })

        if enabled:
            for w in [row, circle, text_lbl]:
                w.config(cursor="hand2")
                w.bind("<Button-1>", lambda e, v=view, pv=parent_view: self.change_view(v, pv))

    def _toggle(self, view):
        data = self.menu_data.get(view)
        if not data or not data["children"]:
            return

        exp = self.expanded.get(view, False)
        self.expanded[view] = not exp

        if exp:
            data["child_frame"].pack_forget()
            if data["arrow"]:
                data["arrow"].config(text="‹")
        else:
            data["child_frame"].pack(fill=X)
            if data["arrow"]:
                data["arrow"].config(text="˅")

    def _set_active(self, view, parent=None):
        for d in self.menu_data.values():
            d["indicator"].configure(background=self.BG)
            for c in d["child_data"]:
                c["indicator"].configure(background=self.BG)
                if c["enabled"]:
                    c["circle"].config(text="○", fg=self.FG_MUTED)

        if parent and parent in self.menu_data:
            self.menu_data[parent]["indicator"].configure(background=self.ACCENT)
            for c in self.menu_data[parent]["child_data"]:
                if c["view"] == view:
                    c["indicator"].configure(background=self.ACCENT)
                    c["circle"].config(text="●", fg=self.ACCENT)
                    break
            if not self.expanded.get(parent, False):
                self._toggle(parent)
        elif view in self.menu_data:
            self.menu_data[view]["indicator"].configure(background=self.ACCENT)

    def change_view(self, view, parent=None):
        self._set_active(view, parent)

        if self.app.content:
            self.app.content.destroy()

        views = {
            "sales": lambda: SalesContent(self.app.content_container, self.app),
            "sales_admin": lambda: SalesAdminContent(self.app.content_container, self.app),
            "reports": lambda: ReportsContent(self.app.content_container, self.app),
            "inventory": lambda: InventoryContent(self.app.content_container, self.app),
            "customers": lambda: CustomersContent(self.app.content_container, self.app),
            "suppliers": lambda: SuppliersContent(self.app.content_container, self.app),
            "supplies": lambda: SuppliesContent(self.app.content_container, self.app),
            "ai_assistant": lambda: AIAssistantContent(self.app.content_container)
        }

        if view in views:
            self.app.content = views[view]()
            self.app.content.pack(fill=BOTH, expand=YES)
