"""
SalesKPIPanel - Tarjetas KPI resumen de ventas
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from app.constants import mexico_now
from app.models import Sale, SaleDetail


class SalesKPIPanel:
    @staticmethod
    def render(tab, db):
        today = mexico_now().date()
        day_start = datetime(today.year, today.month, today.day)
        day_end = day_start + timedelta(days=1)

        week_ago = today - timedelta(days=6)
        week_start = datetime(week_ago.year, week_ago.month, week_ago.day)

        # Ventas hoy
        today_data = db.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total), 0)
        ).filter(Sale.date >= day_start, Sale.date < day_end).first()

        # Ventas esta semana
        week_data = db.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total), 0)
        ).filter(Sale.date >= week_start).first()

        # Ticket promedio
        avg_ticket = db.query(func.avg(Sale.total)).scalar() or 0

        # Productos vendidos hoy
        products_today = db.query(
            func.coalesce(func.sum(SaleDetail.quantity), 0)
        ).join(Sale, SaleDetail.sale_id == Sale.id).filter(
            Sale.date >= day_start, Sale.date < day_end
        ).scalar() or 0

        tab.create_kpi_cards(tab.scrollable_frame, [
            {"title": "Ventas Hoy", "value": f"{today_data[0]} | ${today_data[1]:,.2f}", "color": "#0066cc", "bootstyle": "info"},
            {"title": "Ventas Esta Semana", "value": f"{week_data[0]} | ${week_data[1]:,.2f}", "color": "#28a745", "bootstyle": "success"},
            {"title": "Ticket Promedio", "value": f"${avg_ticket:,.2f}", "color": "#dc3545", "bootstyle": "danger"},
            {"title": "Productos Hoy", "value": f"{products_today:.0f}", "color": "#ffc107", "bootstyle": "warning"},
        ])
