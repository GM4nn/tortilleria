import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.gui.sales.pos.sales.sale_tab import SaleTab
from app.gui.sales.pos.orders.order_tab import OrderTab

class SalesContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Counter to number sales
        self.sale_counter = 0
        
        # Dictionary to save sales tabs {tab_frame: SaleTab}
        self.sale_tabs = {}

        self.setup_ui()

    def setup_ui(self):

        # Create main Notebook (tabs)
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Tab 1: Make Sale (with dynamic sub-tabs)
        self.tab_venta = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_venta, text="  🛒 Hacer Venta  ")
        self.setup_sale_tab()

        # Tab 2: Place an Order
        self.tab_pedido = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pedido, text="  📋 Hacer Pedido  ")
        self.setup_order_tab()


    def setup_sale_tab(self):
        """Configure the Make Sale tab with dynamic sub-tabs"""

        # Container frame for sales notebook
        self.venta_container = ttk.Frame(self.tab_venta)
        self.venta_container.pack(fill=BOTH, expand=YES)

        # Top frame for custom tabs
        self.tabs_header = ttk.Frame(self.venta_container)
        self.tabs_header.pack(fill=X, padx=5, pady=(5, 0))

        # Frame for tab buttons
        self.tabs_buttons_frame = ttk.Frame(self.tabs_header)
        self.tabs_buttons_frame.pack(side=LEFT, fill=X)

        # List to save tab frames (each one contains name + X button)
        self.tab_frames = []
        self.tab_buttons = []
        self.tab_close_buttons = []
        self.current_tab_index = -1

        # Frame container for the content of the tabs
        self.venta_content_frame = ttk.Frame(self.venta_container)
        self.venta_content_frame.pack(fill=BOTH, expand=YES, pady=(5, 0))

        # Create the first sales tab
        self.add_new_sale_tab()

    def add_new_sale_tab(self):

        self.sale_counter += 1
        tab_name = f"Venta #{self.sale_counter}"
        tab_index = len(self.tab_frames)

        # Container frame for the tab (name + X button)
        tab_frame = ttk.Frame(self.tabs_buttons_frame)
        tab_frame.pack(side=LEFT, padx=(0, 2))

        # Button with the name of the tab
        tab_btn = ttk.Button(
            tab_frame,
            text=f" {tab_name} ",
            command=lambda idx=tab_index: self.select_tab(idx),
            bootstyle="primary-outline",
            padding=(12, 6)
        )
        tab_btn.pack(side=LEFT)

        # X button to close
        close_btn = ttk.Button(
            tab_frame,
            text="x",
            command=lambda idx=tab_index: self.close_tab_by_index(idx),
            bootstyle="danger-outline",
            padding=(4, 6),
            width=2
        )
        close_btn.pack(side=LEFT)

        self.tab_frames.append(tab_frame)
        self.tab_buttons.append(tab_btn)
        self.tab_close_buttons.append(close_btn)

        # Relocate the + button (destroy and recreate at the end)
        if hasattr(self, 'btn_add_tab'):
            self.btn_add_tab.destroy()

        self.btn_add_tab = ttk.Button(
            self.tabs_buttons_frame,
            text=" + ",
            command=self.add_new_sale_tab,
            bootstyle="success",
            padding=(8, 6)
        )
        self.btn_add_tab.pack(side=LEFT, padx=(5, 0))

        # Create the actual content of the tab
        sale_tab = SaleTab(self.venta_content_frame, self.app, self)
        self.sale_tabs[str(tab_index)] = sale_tab

        # Select the new tab
        self.select_tab(tab_index)

        # Update X button visibility
        self.update_close_buttons_visibility()

    def select_tab(self, index):

        self.current_tab_index = index

        self.update_tab_styles()
        self.show_current_tab_content()


    def update_tab_styles(self):

        for i, btn in enumerate(self.tab_buttons):

            if i == self.current_tab_index:
                btn.configure(bootstyle="primary")  # Tab active - solid blue
            else:
                btn.configure(bootstyle="primary-outline")  # Tab inactive - border only

    def update_close_buttons_visibility(self):
        
        # Only show X if more than one tab
        show_close = len(self.tab_frames) > 1

        for close_btn in self.tab_close_buttons:
            if show_close:
                close_btn.pack(side=LEFT)
            else:
                close_btn.pack_forget()

    def close_tab_by_index(self, index):

        # Do not close if it is the only tab

        if len(self.tab_frames) <= 1:
            return

        # Check if there are products in the cart
        sale_tab = self.sale_tabs.get(str(index))
        if sale_tab and sale_tab.shopping_cart:
            confirm = mb.askyesno(
                "Confirmar",
                "Esta venta tiene productos en el carrito.\n¿Desea cerrarla de todos modos?"
            )
            if not confirm:
                return

        # Destroy the contents
        if sale_tab:
            sale_tab.destroy()
            del self.sale_tabs[str(index)]

        # Destroy the tab frame (includes button and X)
        self.tab_frames[index].destroy()
        del self.tab_frames[index]
        del self.tab_buttons[index]
        del self.tab_close_buttons[index]

        self.reindex_tabs()

        new_index = min(index, len(self.tab_frames) - 1)
        self.select_tab(new_index)

        self.update_close_buttons_visibility()

    def show_current_tab_content(self):

        # Hide all content
        for sale_tab in self.sale_tabs.values():
            sale_tab.pack_forget()

        # Show only the content of the current tab
        current_index = str(self.current_tab_index)
        if current_index in self.sale_tabs:
            self.sale_tabs[current_index].pack(fill=BOTH, expand=YES)

    def close_sale_tab(self, sale_tab):

        # Do not close if it is the only tab
        if len(self.tab_frames) <= 1:
            return

        # Find the index of the tab to close
        tab_index = None
        for idx, st in self.sale_tabs.items():
            if st == sale_tab:
                tab_index = int(idx)
                break

        if tab_index is not None:

            sale_tab.destroy()
            del self.sale_tabs[str(tab_index)]

            # Destroy frame of the tab
            self.tab_frames[tab_index].destroy()
            del self.tab_frames[tab_index]
            del self.tab_buttons[tab_index]
            del self.tab_close_buttons[tab_index]

            self.reindex_tabs()

            # select other tab
            new_index = min(tab_index, len(self.tab_frames) - 1)
            self.select_tab(new_index)

            self.update_close_buttons_visibility()


    def reindex_tabs(self):
        """Reindex the tabs after closing one"""

        new_sale_tabs = {}
    
        for i, (_, sale_tab) in enumerate(sorted(self.sale_tabs.items(), key=lambda x: int(x[0]))):
            new_sale_tabs[str(i)] = sale_tab
    
        self.sale_tabs = new_sale_tabs

        for i, btn in enumerate(self.tab_buttons):
            btn.configure(command=lambda idx=i: self.select_tab(idx))
        for i, close_btn in enumerate(self.tab_close_buttons):
            close_btn.configure(command=lambda idx=i: self.close_tab_by_index(idx))

    def setup_order_tab(self):
        self.order_tab = OrderTab(self.tab_pedido, self.app, self)
        self.order_tab.pack(fill=BOTH, expand=YES)

