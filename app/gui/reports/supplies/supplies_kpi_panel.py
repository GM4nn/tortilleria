"""
SuppliesKPIPanel - Tarjetas KPI resumen de insumos
"""

from sqlalchemy import func
from app.models import Supply, SupplyPurchase


class SuppliesKPIPanel:
    @staticmethod
    def render(tab, db):
        # Total invertido
        total_invested = db.query(
            func.coalesce(func.sum(SupplyPurchase.total_price), 0)
        ).scalar() or 0

        # Compras realizadas
        total_purchases = db.query(func.count(SupplyPurchase.id)).scalar() or 0

        # Insumos registrados
        total_supplies = db.query(func.count(Supply.id)).scalar() or 0

        # Proveedores activos (que tienen compras)
        active_suppliers = db.query(
            func.count(func.distinct(SupplyPurchase.supplier_id))
        ).scalar() or 0

        tab.create_kpi_cards(tab.scrollable_frame, [
            {"title": "Total Invertido", "value": f"${total_invested:,.2f}", "color": "#0066cc", "bootstyle": "info"},
            {"title": "Compras Realizadas", "value": str(total_purchases), "color": "#28a745", "bootstyle": "success"},
            {"title": "Insumos Registrados", "value": str(total_supplies), "color": "#dc3545", "bootstyle": "danger"},
            {"title": "Proveedores Activos", "value": str(active_suppliers), "color": "#ffc107", "bootstyle": "warning"},
        ])
