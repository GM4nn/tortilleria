"""
OrdersByCustomerSection - Tabla completa de pedidos por cliente
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlalchemy import func
from app.models import Customer, Order
from .customer_products_dialog import CustomerProductsDialog


class OrdersByCustomerSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "👤 Pedidos por Cliente",
            "Detalle de pedidos por cliente (haz clic en Ver Productos para mas detalles)",
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

        # Header
        header_frame = ttk.Frame(section)
        header_frame.pack(fill=X, pady=(0, 5))
        for text, w in [("Cliente", 25), ("Categoria", 15), ("Pedidos", 12), ("Total", 18), ("Acciones", 15)]:
            ttk.Label(header_frame, text=text, font=("Segoe UI", 10, "bold"), width=w).pack(side=LEFT, padx=5)

        for customer in customer_orders:
            row_frame = ttk.Frame(section)
            row_frame.pack(fill=X, pady=2)

            ttk.Label(row_frame, text=customer.customer_name, width=25).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=customer.customer_category or "N/A", width=15).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=str(customer.orders), width=12).pack(side=LEFT, padx=5)
            ttk.Label(
                row_frame, text=f"${customer.total:,.2f}", width=18,
                foreground="#28a745", font=("Segoe UI", 10, "bold")
            ).pack(side=LEFT, padx=5)

            ttk.Button(
                row_frame, text="📋 Ver Productos",
                bootstyle="outline-info", width=15,
                command=lambda cid=customer.id, cname=customer.customer_name: CustomerProductsDialog.show(tab, cid, cname)
            ).pack(side=LEFT, padx=5)
