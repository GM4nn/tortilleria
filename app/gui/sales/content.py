import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.gui.sales.products import Products
from app.gui.sales.shopping_car import ShoppingCar
from app.data.providers.inventory import inventory_provider
from app.data.providers.sales import sale_provider


class SalesContent(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # shopping cart vars
        self.shopping_cart = []
        self.total = 0.0
        
        self.inventory_provider = inventory_provider
        self.sales_provider = sale_provider

        # products vars
        self.products_items = []
        
        self.setup_ui()
    
    def setup_ui(self):
        
        #  Central Panel (products)
        self.products = Products(self, self.app, self)
        self.products.pack(side=LEFT, fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Right Panel (shopping car)
        self.shopping_cart_gui = ShoppingCar(self, self.app, self)
        self.shopping_cart_gui.pack(side=LEFT, fill=Y, padx=(0, 10), pady=10)
    
    # shopping cart methods
    def add_product_to_car(self, product):

        # if already exists
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

    def delete_product_from_car(self, index):
        if 0 <= index < len(self.shopping_cart):
            del self.shopping_cart[index]
            self.shopping_cart_gui.refresh_shopping_car()

    def get_total(self):
        self.total = sum(item['subtotal'] for item in self.shopping_cart)
        return self.total

    def clean_shopping_car(self):
        """Vaciar el carrito"""
        self.shopping_cart = []
        self.total = 0.0
        self.shopping_cart_gui.refresh_shopping_car()

    def charge(self):

        if not self.shopping_cart:
            mb.showwarning("Carrito vacío", "No hay productos en el carrito")
            return

        success, result = self.sales_provider.save(self.shopping_cart, self.total)

        if success:
            mb.showinfo(
                "Venta Completada",
                f"Venta #{result} registrada\n\nTotal: ${self.total:.2f}"
            )
            self.clean_shopping_car()
            
        else:
            mb.showerror("Error", f"Error al guardar venta:\n{result}")

    # products methods
    def get_products(self):
        self.products_items = self.inventory_provider.get_all()