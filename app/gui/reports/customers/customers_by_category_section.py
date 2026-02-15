"""
CustomersByCategorySection - Desglose por categoria (Mostrador, Comedor, Tienda)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlalchemy import func
from app.models import Customer, Order


class CustomersByCategorySection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "📊 Clientes por Categoria",
            "Distribucion de clientes y pedidos por tipo",
            bootstyle="info"
        )

        data = db.query(
            Customer.customer_category,
            func.count(func.distinct(Customer.id)).label('num_customers'),
            func.count(Order.id).label('num_orders'),
            func.coalesce(func.sum(Order.total), 0).label('total')
        ).join(
            Order, Customer.id == Order.customer_id
        ).filter(
            Customer.active == True,
            Customer.active2 == True
        ).group_by(
            Customer.customer_category
        ).order_by(
            func.sum(Order.total).desc()
        ).all()

        if not data:
            tab.create_empty_state(section, "No hay clientes registrados")
            return

        cards_frame = ttk.Frame(section)
        cards_frame.pack(fill=X)

        colors = {"Mostrador": "#17a2b8", "Comedor": "#28a745", "Tienda": "#ffc107"}
        styles = {"Mostrador": "info", "Comedor": "success", "Tienda": "warning"}

        for i, row in enumerate(data):
            category = row.customer_category or "Sin Categoria"
            color = colors.get(category, "#6c757d")
            style = styles.get(category, "secondary")

            card = ttk.Labelframe(cards_frame, text=category, padding=15, bootstyle=style)
            padx = (0, 10) if i < len(data) - 1 else (0, 0)
            if i > 0:
                padx = (10, 10) if i < len(data) - 1 else (10, 0)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=padx)

            ttk.Label(card, text=f"{row.num_customers} clientes", font=("Segoe UI", 12, "bold"), foreground=color).pack(anchor=W)
            ttk.Label(card, text=f"{row.num_orders} pedidos", font=("Segoe UI", 10)).pack(anchor=W, pady=(5, 0))
            ttk.Label(card, text=f"${row.total:,.2f}", font=("Segoe UI", 14, "bold"), foreground=color).pack(anchor=W, pady=(5, 0))
