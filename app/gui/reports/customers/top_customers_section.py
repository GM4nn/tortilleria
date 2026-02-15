"""
TopCustomersSection - Top 5 clientes mas fieles
"""

from sqlalchemy import func
from app.models import Customer, Order, OrderDetail


class TopCustomersSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "🏅 Clientes Mas Fieles",
            "Top 5 clientes con mayor cantidad de productos pedidos",
            bootstyle="info"
        )

        top_customers = db.query(
            Customer.id,
            Customer.customer_name,
            Customer.customer_category,
            func.count(func.distinct(Order.id)).label('orders'),
            func.sum(OrderDetail.quantity).label('total_products'),
        ).join(
            Order, Customer.id == Order.customer_id
        ).join(
            OrderDetail, Order.id == OrderDetail.order_id
        ).filter(
            Customer.active == True,
            Customer.active2 == True
        ).group_by(
            Customer.id, Customer.customer_name, Customer.customer_category
        ).order_by(
            func.sum(OrderDetail.quantity).desc()
        ).limit(5).all()

        if not top_customers:
            tab.create_empty_state(section, "No hay pedidos registrados de clientes")
            return

        # Get total spent per customer (separate query to avoid duplication from join)
        customer_totals = {}
        for customer in top_customers:
            total = db.query(func.sum(Order.total)).filter(
                Order.customer_id == customer.id
            ).scalar() or 0
            customer_totals[customer.id] = total

        headers = [("Cliente", 25), ("Categoria", 15), ("Pedidos", 12), ("Productos", 12), ("Total Gastado", 18)]
        rows = []
        for i, c in enumerate(top_customers):
            icon = "🏆 " if i == 0 else ""
            rows.append([
                f"{icon}{c.customer_name}",
                c.customer_category or "N/A",
                str(c.orders),
                f"{c.total_products:.0f}",
                f"${customer_totals[c.id]:,.2f}"
            ])

        tab.create_table(section, headers, rows, money_cols={4})
