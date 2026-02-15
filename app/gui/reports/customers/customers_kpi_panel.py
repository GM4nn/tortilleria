"""
CustomersKPIPanel - Tarjetas KPI resumen de clientes
"""

from sqlalchemy import func
from app.models import Customer, Order


class CustomersKPIPanel:
    @staticmethod
    def render(tab, db):
        # Total pedidos de clientes
        total_orders = db.query(func.count(Order.id)).join(
            Customer, Order.customer_id == Customer.id
        ).filter(
            Customer.active == True,
            Customer.active2 == True
        ).scalar() or 0

        # Clientes con pedidos (los que realmente han pedido)
        customers_with_orders = db.query(
            func.count(func.distinct(Order.customer_id))
        ).join(Customer, Order.customer_id == Customer.id).filter(
            Customer.active == True,
            Customer.active2 == True
        ).scalar() or 0

        # Gasto promedio por cliente
        avg_subq = db.query(
            func.sum(Order.total).label('customer_total')
        ).join(Customer, Order.customer_id == Customer.id).filter(
            Customer.active == True,
            Customer.active2 == True
        ).group_by(Order.customer_id).subquery()

        avg_spent = db.query(func.avg(avg_subq.c.customer_total)).scalar() or 0

        # Cliente mas valioso
        top_customer = db.query(
            Customer.customer_name,
            func.sum(Order.total).label('total')
        ).join(Order, Customer.id == Order.customer_id).filter(
            Customer.active == True,
            Customer.active2 == True
        ).group_by(Customer.id, Customer.customer_name).order_by(
            func.sum(Order.total).desc()
        ).first()

        top_name = top_customer.customer_name if top_customer else "N/A"

        tab.create_kpi_cards(tab.scrollable_frame, [
            {"title": "Total Pedidos", "value": str(total_orders), "color": "#0066cc", "bootstyle": "info"},
            {"title": "Clientes con Pedidos", "value": str(customers_with_orders), "color": "#28a745", "bootstyle": "success"},
            {"title": "Gasto Promedio", "value": f"${avg_spent:,.2f}", "color": "#dc3545", "bootstyle": "danger"},
            {"title": "Cliente Top", "value": top_name, "color": "#ffc107", "bootstyle": "warning"},
        ])
