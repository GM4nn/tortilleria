"""
SalesKPIPanel - Tarjetas KPI resumen de ventas
"""

from datetime import timedelta
from sqlalchemy import func
from app.constants import mexico_now
from app.models import Sale, SaleDetail


class SalesKPIPanel:
    @staticmethod
    def render(tab, db):
        today = mexico_now().date()
        week_ago = today - timedelta(days=6)

        # Ventas hoy
        today_data = db.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total), 0)
        ).filter(func.date(Sale.date) == today).first()

        # Ventas esta semana
        week_data = db.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total), 0)
        ).filter(func.date(Sale.date) >= week_ago).first()

        # Ticket promedio
        avg_ticket = db.query(func.avg(Sale.total)).scalar() or 0

        # Productos vendidos hoy
        products_today = db.query(
            func.coalesce(func.sum(SaleDetail.quantity), 0)
        ).join(Sale, SaleDetail.sale_id == Sale.id).filter(
            func.date(Sale.date) == today
        ).scalar() or 0

        tab.create_kpi_cards(tab.scrollable_frame, [
            {"title": "Ventas Hoy", "value": f"{today_data[0]} | ${today_data[1]:,.2f}", "color": "#0066cc", "bootstyle": "info"},
            {"title": "Ventas Esta Semana", "value": f"{week_data[0]} | ${week_data[1]:,.2f}", "color": "#28a745", "bootstyle": "success"},
            {"title": "Ticket Promedio", "value": f"${avg_ticket:,.2f}", "color": "#dc3545", "bootstyle": "danger"},
            {"title": "Productos Hoy", "value": f"{products_today:.0f}", "color": "#ffc107", "bootstyle": "warning"},
        ])
