import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.data.providers.customers import customer_provider
from app.data.providers.inventory import inventory_provider
from app.data.providers.orders import order_provider
from app.gui.sales.pos.orders.customers_panel import CustomersPanel
from app.gui.sales.pos.orders.products_panel import ProductsPanel
from app.gui.sales.pos.orders.order_summary_panel import OrderSummaryPanel


class OrderTab(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content
        self.selected_customer = None
        self.order_items = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Panel izquierdo: Lista de clientes
        self.customers_panel = CustomersPanel(
            main_container, on_customer_selected=self.select_customer
        )
        self.customers_panel.pack(side=LEFT, fill=Y, padx=(0, 10))

        # Panel central: Productos
        self.products_panel = ProductsPanel(
            main_container, on_product_added=self.add_to_order
        )
        self.products_panel.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Panel derecho: Resumen del pedido
        self.summary_panel = OrderSummaryPanel(
            main_container,
            on_save=self.save_order,
            on_clear=self.clear_order,
            on_remove_item=self.remove_from_order
        )
        self.summary_panel.pack(side=LEFT, fill=Y)

    def load_data(self):
        customers = customer_provider.get_all()
        products = inventory_provider.get_all()
        self.customers_panel.load(customers)
        self.products_panel.load(products)

    def select_customer(self, customer):
        self.selected_customer = customer
        self.customers_panel.set_selected(customer)
        self.summary_panel.set_customer(customer.customer_name)
        self.products_panel.show_for_customer(customer.customer_name, customer.id)
        self._update_save_state()

    def add_to_order(self, product_id, name, price_var, qty_var):
        try:
            price = float(price_var.get())
            quantity = float(qty_var.get())

            if price <= 0 or quantity <= 0:
                mb.showwarning("Error", "El precio y cantidad deben ser mayores a 0")
                return

            # Buscar si ya existe en el pedido, reemplazar cantidad
            for item in self.order_items:
                if item['id'] == product_id and item['price'] == price:
                    item['quantity'] = quantity
                    item['subtotal'] = quantity * item['price']
                    self._refresh_summary()
                    return

            self.order_items.append({
                'id': product_id,
                'name': name,
                'price': price,
                'quantity': quantity,
                'subtotal': price * quantity
            })

            self._refresh_summary()
            qty_var.set("1")

        except ValueError:
            mb.showwarning("Error", "Ingrese valores numéricos válidos")

    def remove_from_order(self, index):
        if 0 <= index < len(self.order_items):
            del self.order_items[index]
            self._refresh_summary()

    def save_order(self):
        if not self.selected_customer:
            mb.showwarning("Error", "Seleccione un cliente")
            return

        if not self.order_items:
            mb.showwarning("Error", "Agregue productos al pedido")
            return

        total = sum(item['subtotal'] for item in self.order_items)

        success, result = order_provider.save(
            items=self.order_items,
            total=total,
            customer_id=self.selected_customer.id
        )

        if success:
            mb.showinfo(
                "Pedido Guardado",
                f"Pedido #{result} guardado correctamente\n\n"
                f"Cliente: {self.selected_customer.customer_name}\n"
                f"Total: ${total:.2f}"
            )
            self.clear_order()
        else:
            mb.showerror("Error", f"Error al guardar pedido:\n{result}")

    def clear_order(self):
        self.order_items = []
        self.selected_customer = None
        self.customers_panel.clear_selection()
        self.products_panel.hide_products()
        self.summary_panel.clear_customer()
        self._refresh_summary()

    def _refresh_summary(self):
        self.summary_panel.refresh(self.order_items)
        self._update_save_state()

    def _update_save_state(self):
        enabled = bool(self.selected_customer and self.order_items)
        self.summary_panel.set_save_enabled(enabled)
