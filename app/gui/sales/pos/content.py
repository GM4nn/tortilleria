import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.gui.sales.pos.sales.sale_tab import SaleTab
from app.gui.sales.pos.orders.order_tab import OrderTab

class SalesContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Contador para numerar las ventas
        self.sale_counter = 0
        # Diccionario para guardar las tabs de venta {tab_frame: SaleTab}
        self.sale_tabs = {}

        self.setup_ui()

    def setup_ui(self):
        # Crear Notebook principal (tabs)
        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Tab 1: Hacer Venta (con sub-tabs dinamicas)
        self.tab_venta = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_venta, text="  🛒 Hacer Venta  ")
        self.setup_venta_tab()

        # Tab 2: Hacer Pedido
        self.tab_pedido = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pedido, text="  📋 Hacer Pedido  ")
        self.setup_pedido_tab()


    def setup_venta_tab(self):
        """Configurar el tab de Hacer Venta con sub-tabs dinamicas"""

        # Frame contenedor para el notebook de ventas
        self.venta_container = ttk.Frame(self.tab_venta)
        self.venta_container.pack(fill=BOTH, expand=YES)

        # Frame superior para las tabs personalizadas
        self.tabs_header = ttk.Frame(self.venta_container)
        self.tabs_header.pack(fill=X, padx=5, pady=(5, 0))

        # Frame para los botones de tabs
        self.tabs_buttons_frame = ttk.Frame(self.tabs_header)
        self.tabs_buttons_frame.pack(side=LEFT, fill=X)

        # Lista para guardar los frames de tabs (cada uno contiene nombre + boton X)
        self.tab_frames = []
        self.tab_buttons = []
        self.tab_close_buttons = []
        self.current_tab_index = -1

        # Frame contenedor para el contenido de las tabs
        self.venta_content_frame = ttk.Frame(self.venta_container)
        self.venta_content_frame.pack(fill=BOTH, expand=YES, pady=(5, 0))

        # Crear la primera tab de venta
        self.add_new_sale_tab()

    def add_new_sale_tab(self):
        """Agregar una nueva tab de venta"""

        self.sale_counter += 1
        tab_name = f"Venta #{self.sale_counter}"
        tab_index = len(self.tab_frames)

        # Frame contenedor para la tab (nombre + boton X)
        tab_frame = ttk.Frame(self.tabs_buttons_frame)
        tab_frame.pack(side=LEFT, padx=(0, 2))

        # Boton con el nombre de la tab
        tab_btn = ttk.Button(
            tab_frame,
            text=f" {tab_name} ",
            command=lambda idx=tab_index: self.select_tab(idx),
            bootstyle="primary-outline",
            padding=(12, 6)
        )
        tab_btn.pack(side=LEFT)

        # Boton X para cerrar
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

        # Reubicar el boton + (destruir y recrear al final)
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

        # Crear el contenido real de la tab
        sale_tab = SaleTab(self.venta_content_frame, self.app, self, self.sale_counter)
        self.sale_tabs[str(tab_index)] = sale_tab

        # Seleccionar la nueva tab
        self.select_tab(tab_index)

        # Actualizar visibilidad de botones X
        self.update_close_buttons_visibility()

    def select_tab(self, index):
        """Seleccionar una tab por su indice"""
        self.current_tab_index = index

        self.update_tab_styles()
        self.show_current_tab_content()

    def update_tab_styles(self):
        """Actualizar estilos de los botones de tabs"""
        for i, btn in enumerate(self.tab_buttons):
            if i == self.current_tab_index:
                btn.configure(bootstyle="primary")  # Tab activa - azul solido
            else:
                btn.configure(bootstyle="primary-outline")  # Tab inactiva - solo borde

    def update_close_buttons_visibility(self):
        """Mostrar/ocultar botones X segun cantidad de tabs"""
        # Solo mostrar X si hay mas de una tab
        show_close = len(self.tab_frames) > 1
        for close_btn in self.tab_close_buttons:
            if show_close:
                close_btn.pack(side=LEFT)
            else:
                close_btn.pack_forget()

    def close_tab_by_index(self, index):
        """Cerrar una tab por su indice"""
        # No cerrar si es la unica tab
        if len(self.tab_frames) <= 1:
            return

        # Verificar si hay productos en el carrito
        sale_tab = self.sale_tabs.get(str(index))
        if sale_tab and sale_tab.shopping_cart:
            confirm = mb.askyesno(
                "Confirmar",
                "Esta venta tiene productos en el carrito.\n¿Desea cerrarla de todos modos?"
            )
            if not confirm:
                return

        # Destruir el contenido
        if sale_tab:
            sale_tab.destroy()
            del self.sale_tabs[str(index)]

        # Destruir el frame de la tab (incluye boton y X)
        self.tab_frames[index].destroy()
        del self.tab_frames[index]
        del self.tab_buttons[index]
        del self.tab_close_buttons[index]

        # Reindexar las tabs restantes
        self.reindex_tabs()

        # Seleccionar otra tab
        new_index = min(index, len(self.tab_frames) - 1)
        self.select_tab(new_index)

        # Actualizar visibilidad de botones X
        self.update_close_buttons_visibility()

    def show_current_tab_content(self):
        """Mostrar el contenido de la tab actualmente seleccionada"""

        # Ocultar todos los contenidos
        for sale_tab in self.sale_tabs.values():
            sale_tab.pack_forget()

        # Mostrar solo el contenido de la tab actual
        current_index = str(self.current_tab_index)
        if current_index in self.sale_tabs:
            self.sale_tabs[current_index].pack(fill=BOTH, expand=YES)

    def close_sale_tab(self, sale_tab):
        """Cerrar una tab de venta despues de cobrar"""
        # No cerrar si es la unica tab
        if len(self.tab_frames) <= 1:
            return

        # Encontrar el indice de la tab a cerrar
        tab_index = None
        for idx, st in self.sale_tabs.items():
            if st == sale_tab:
                tab_index = int(idx)
                break

        if tab_index is not None:
            # Destruir el contenido
            sale_tab.destroy()
            del self.sale_tabs[str(tab_index)]

            # Destruir el frame de la tab
            self.tab_frames[tab_index].destroy()
            del self.tab_frames[tab_index]
            del self.tab_buttons[tab_index]
            del self.tab_close_buttons[tab_index]

            # Reindexar las tabs restantes
            self.reindex_tabs()

            # Seleccionar otra tab
            new_index = min(tab_index, len(self.tab_frames) - 1)
            self.select_tab(new_index)

            # Actualizar visibilidad de botones X
            self.update_close_buttons_visibility()

    def reindex_tabs(self):
        """Reindexar las tabs despues de cerrar una"""
        # Reindexar sale_tabs
        new_sale_tabs = {}
        for i, (_, sale_tab) in enumerate(sorted(self.sale_tabs.items(), key=lambda x: int(x[0]))):
            new_sale_tabs[str(i)] = sale_tab
        self.sale_tabs = new_sale_tabs

        # Actualizar comandos de los botones de nombre y cerrar
        for i, btn in enumerate(self.tab_buttons):
            btn.configure(command=lambda idx=i: self.select_tab(idx))
        for i, close_btn in enumerate(self.tab_close_buttons):
            close_btn.configure(command=lambda idx=i: self.close_tab_by_index(idx))

    def setup_pedido_tab(self):
        """Configurar el tab de Hacer Pedido"""
        self.order_tab = OrderTab(self.tab_pedido, self.app, self)
        self.order_tab.pack(fill=BOTH, expand=YES)

