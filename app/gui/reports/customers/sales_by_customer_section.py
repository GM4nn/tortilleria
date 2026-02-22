"""
OrdersByCustomerSection - Tabla completa de pedidos por cliente
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from sqlalchemy import func
from app.models import Customer, Order


class OrdersByCustomerSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "👤 Pedidos por Cliente",
            "Detalle de pedidos por cliente",
            bootstyle="info"
        )

        customer_orders = db.query(
            Customer.id,
            Customer.customer_name,
            Customer.customer_category,
            func.count(Order.id).label('orders'),
            func.sum(Order.total).label('total')
        ).join(
            Order, Customer.id == Order.customer_id
        ).filter(
            Customer.active == True,
            Customer.active2 == True
        ).group_by(
            Customer.id, Customer.customer_name, Customer.customer_category
        ).order_by(
            func.sum(Order.total).desc()
        ).all()

        if not customer_orders:
            tab.create_empty_state(section, "No hay pedidos registrados de clientes")
            return

        columns = [
            {"text": "#", "stretch": False, "width": 50},
            {"text": "Cliente", "stretch": True},
            {"text": "Categoria", "stretch": False, "width": 120},
            {"text": "Pedidos", "stretch": False, "width": 90},
            {"text": "Total", "stretch": False, "width": 140},
        ]

        rows = []
        for i, customer in enumerate(customer_orders):
            rows.append([
                i + 1,
                customer.customer_name,
                customer.customer_category or "N/A",
                customer.orders,
                f"${customer.total:,.2f}",
            ])

        table_frame = ttk.Frame(section)
        table_frame.pack(fill=BOTH, expand=YES)

        table = Tableview(
            master=table_frame,
            coldata=columns,
            rowdata=rows,
            paginated=False,
            searchable=False,
            bootstyle=INFO,
            height=min(len(rows), 15),
        )
        table.pack(fill=BOTH, expand=YES)
        table.view.configure(selectmode="none")
