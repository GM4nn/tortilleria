import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.constants import ORDER_STATUSES_ALL
from app.data.providers.orders import order_provider
from app.data.providers.customers import customer_provider
from app.gui.sales.admin_sales.orders.orders_header_with_filters import OrdersHeaderWithFilters
from app.gui.sales.admin_sales.orders.orders_list import OrdersList
from app.gui.sales.admin_sales.orders.detail_order import DetailOrder


class OrderContent(ttk.Frame):
    def __init__(self, parent, app, content):
        super().__init__(parent)
        self.app = app
        self.content = content
        self._filters = None
        self.customers_cache = {}

        self.setup_ui()
        self.load_orders()

    def setup_ui(self):

        # Header con filtros
        self.header = OrdersHeaderWithFilters(
            self,
            on_refresh=self.load_orders,
            on_filter=self.filter_orders
        )
        self.header.pack(fill=X)

        # Contenedor principal: lista (izquierda) + detalle (derecha)
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))

        # Lista de pedidos
        self.orders_list = OrdersList(
            main_container,
            customers_cache=self.customers_cache,
            on_select=self.on_order_select,
            on_page_change=self.display_current_page,
            pagesize=10
        )
        self.orders_list.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Detalle del pedido
        self.detail_order = DetailOrder(
            main_container,
            customers_cache=self.customers_cache,
            on_order_changed=self.load_orders
        )
        self.detail_order.pack(side=LEFT, fill=Y)

    def load_orders(self):
        self.load_customers_cache()
        self.header.load_customers()
        self.filter_orders()

    def load_customers_cache(self):
        customers = customer_provider.get_all()
        self.customers_cache.clear()
        for c in customers:
            self.customers_cache[c.id] = c.customer_name

    def filter_orders(self):
        status_filter = self.header.get_status_filter()
        customer_filter = self.header.get_customer_filter()

        filters = []
        if status_filter != ORDER_STATUSES_ALL:
            filters += order_provider.build_status_filter(status_filter)
        if customer_filter:
            filters += order_provider.build_customer_filter(customer_filter)

        self._filters = filters or None
        self.orders_list.pagination.reset()
        self.orders_list.pagination.update_total(order_provider.get_count(self._filters))
        self.display_current_page()

    def display_current_page(self):
        pagination = self.orders_list.pagination
        offset = pagination.get_offset()
        orders = order_provider.get_all(offset, pagination._pagesize, self._filters)
        self.orders_list.display_orders(orders)

    def on_order_select(self, order):
        self.detail_order.show_order_details(order)
