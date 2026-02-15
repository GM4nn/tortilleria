"""
OrdersByStatusSection - Resumen de pedidos por estado (pendiente, completado, cancelado)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlalchemy import func
from app.models import Order


STATUS_CONFIG = {
    "pendiente": {"label": "Pendientes", "color": "#ffc107", "bootstyle": "warning"},
    "completado": {"label": "Completados", "color": "#28a745", "bootstyle": "success"},
    "cancelado": {"label": "Cancelados", "color": "#dc3545", "bootstyle": "danger"},
}


class OrdersByStatusSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "📋 Pedidos por Estado",
            "Distribucion de pedidos segun su estado actual",
            bootstyle="primary"
        )

        data = db.query(
            Order.status,
            func.count(Order.id).label('count'),
            func.coalesce(func.sum(Order.total), 0).label('total')
        ).group_by(Order.status).all()

        if not data:
            tab.create_empty_state(section, "No hay pedidos registrados")
            return

        cards_frame = ttk.Frame(section)
        cards_frame.pack(fill=X)

        status_map = {row.status: row for row in data}

        for i, (status, cfg) in enumerate(STATUS_CONFIG.items()):
            row = status_map.get(status)
            count = row.count if row else 0
            total = row.total if row else 0

            card = ttk.Labelframe(cards_frame, text=cfg["label"], padding=15, bootstyle=cfg["bootstyle"])
            padx = (0, 10) if i < len(STATUS_CONFIG) - 1 else (0, 0)
            if i > 0:
                padx = (10, 10) if i < len(STATUS_CONFIG) - 1 else (10, 0)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=padx)

            ttk.Label(card, text=str(count), font=("Segoe UI", 22, "bold"), foreground=cfg["color"]).pack(anchor=W)
            ttk.Label(card, text="pedidos", font=("Segoe UI", 10), foreground="#6c757d").pack(anchor=W)
            ttk.Label(card, text=f"${total:,.2f}", font=("Segoe UI", 14, "bold"), foreground=cfg["color"]).pack(anchor=W, pady=(8, 0))
