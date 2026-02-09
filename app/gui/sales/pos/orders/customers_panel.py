import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class CustomersPanel(ttk.Labelframe):
    
    def __init__(self, parent, on_customer_selected):
        
        super().__init__(parent, text="  Seleccionar Cliente  ", padding=10, width=280)

        self.on_customer_selected = on_customer_selected
        self.selected_customer = None
        self.customers_list = []

        self.pack_propagate(False)
        self.setup_ui()

    def setup_ui(self):

        self.setup_gui_search_bar()
        self.setup_gui_customer_list_with_scroll()


    def setup_gui_search_bar(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(search_frame, text="Buscar:").pack(side=LEFT)

        self.search_var = ttk.StringVar()
        self.search_var.trace_add('write', self._on_filter)

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=LEFT, fill=X, expand=YES, padx=(5, 0))

    def setup_gui_customer_list_with_scroll(self):

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=BOTH, expand=YES)

        self.canvas = ttk.Canvas(list_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.canvas.yview)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.scrollbar.pack(side=RIGHT, fill=Y)

    def load(self, customers):
        self.customers_list = customers
        self.display()

    def display(self, filter_text=""):

        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        filtered = self.customers_list

        if filter_text:
            filtered = [
                c for c in self.customers_list
                if filter_text.lower() in (c.customer_name or '').lower()
            ]

        if not filtered:
            ttk.Label(
                self.inner_frame, text="No se encontraron clientes", bootstyle="secondary"
            ).pack(pady=20)
            return

        for customer in filtered:
            self._create_card(customer)

    def set_selected(self, customer):
        self.selected_customer = customer
        self.display(self.search_var.get())

    def clear_selection(self):
        self.selected_customer = None
        self.display()

    def _create_card(self, customer):
        is_selected = self.selected_customer and self.selected_customer.id == customer.id
        style = "info" if is_selected else "light"

        card = ttk.Frame(self.inner_frame, bootstyle=style, relief="solid", borderwidth=1)
        card.pack(fill=X, pady=2)

        content = ttk.Frame(card)
        content.pack(fill=X, padx=10, pady=8)

        name_label = ttk.Label(content, text=customer.customer_name, font=("Arial", 11, "bold"))
        name_label.pack(anchor=W)

        if customer.customer_category:
            cat_label = ttk.Label(
                content, text=customer.customer_category, font=("Arial", 9), bootstyle="secondary"
            )
            cat_label.pack(anchor=W)

        for widget in [card, content, name_label]:
            widget.bind("<Button-1>", lambda e, c=customer: self.on_customer_selected(c))
            widget.configure(cursor="hand2")

    def _on_filter(self, *args):
        self.display(self.search_var.get())

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
