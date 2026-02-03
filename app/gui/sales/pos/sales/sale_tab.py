import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.gui.sales.pos.sales.products import Products
from app.gui.sales.pos.sales.shopping_car import ShoppingCar
from app.data.providers.inventory import inventory_provider
from app.data.providers.sales import sale_provider


class SaleTab(ttk.Frame):
    """Tab individual para una venta en progreso"""

    def __init__(self, parent, app, tab_manager, tab_number):
        super().__init__(parent)
        self.app = app
        self.tab_manager = tab_manager  # Referencia al contenedor de tabs
        self.tab_number = tab_number

        # Cada tab tiene su propio carrito
        self.shopping_cart = []
        self.total = 0.0

        self.inventory_provider = inventory_provider
        self.sales_provider = sale_provider

        # Products vars
        self.products_items = []

        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de la tab de venta"""
        # Panel de productos (izquierda)
        self.products = Products(self, self.app, self)
        self.products.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)

        # Panel del carrito (derecha)
        self.shopping_cart_gui = ShoppingCar(self, self.app, self)
        self.shopping_cart_gui.pack(side=LEFT, fill=Y, padx=(0, 10), pady=10)

    # Shopping cart methods
    def add_product_to_car(self, product):
        # Si ya existe, incrementar cantidad
        for item in self.shopping_cart:
            if item['id'] == product['id']:
                item['quantity'] += 1
                item['subtotal'] = item['quantity'] * item['price']
                self.shopping_cart_gui.refresh_shopping_car()
                return

        self.shopping_cart.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': 1,
            'subtotal': product['price']
        })

        self.shopping_cart_gui.refresh_shopping_car()

    def remove_one_from_car(self, product_id):
        for item in self.shopping_cart:
            if item['id'] == product_id:
                item['quantity'] -= 1
                if item['quantity'] <= 0:
                    self.shopping_cart.remove(item)
                else:
                    item['subtotal'] = item['quantity'] * item['price']
                self.shopping_cart_gui.refresh_shopping_car()
                return

    def delete_product_from_car(self, index):
        if 0 <= index < len(self.shopping_cart):
            del self.shopping_cart[index]
            self.shopping_cart_gui.refresh_shopping_car()
            self.products.show_products()

    def get_total(self):
        self.total = sum(item['subtotal'] for item in self.shopping_cart)
        return self.total

    def clean_shopping_car(self):
        """Vaciar el carrito"""
        self.shopping_cart = []
        self.total = 0.0
        self.shopping_cart_gui.refresh_shopping_car()
        self.products.show_products()

    def charge(self):
        if not self.shopping_cart:
            mb.showwarning("Carrito vacio", "No hay productos en el carrito")
            return

        # Siempre usar cliente Mostrador para ventas directas
        customer_id = self.shopping_cart_gui.get_mostrador_customer_id()

        if not customer_id:
            mb.showerror("Error", "No se pudo obtener el cliente Mostrador. Por favor, verifique que exista en la base de datos.")
            return

        success, result = self.sales_provider.save(self.shopping_cart, self.total, customer_id)

        if success:
            mb.showinfo(
                "Venta Completada",
                f"Venta #{result} registrada\n\nTotal: ${self.total:.2f}"
            )
            self.clean_shopping_car()
            # Cerrar esta tab despues de cobrar si hay mas de una
            self.tab_manager.close_sale_tab(self)
        else:
            mb.showerror("Error", f"Error al guardar venta:\n{result}")

    # Products methods
    def get_products(self):
        self.products_items = self.inventory_provider.get_all()
