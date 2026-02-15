"""
SuppliersKPIPanel - Tarjetas KPI resumen de proveedores
"""

from sqlalchemy import func
from app.models import Supplier, SupplyPurchase


class SuppliersKPIPanel:
    @staticmethod
    def render(tab, db):
        # Total proveedores activos
        total_suppliers = db.query(func.count(Supplier.id)).filter(
            Supplier.active == True
        ).scalar() or 0

        # Total comprado a proveedores
        total_purchased = db.query(
            func.coalesce(func.sum(SupplyPurchase.total_price), 0)
        ).scalar() or 0

        # Precio promedio por compra
        avg_price = db.query(
            func.avg(SupplyPurchase.unit_price)
        ).scalar() or 0

        # Proveedor top (mas compras)
        top_supplier = db.query(
            Supplier.supplier_name,
            func.count(SupplyPurchase.id).label('purchases')
        ).join(
            SupplyPurchase, Supplier.id == SupplyPurchase.supplier_id
        ).group_by(
            Supplier.id, Supplier.supplier_name
        ).order_by(
            func.count(SupplyPurchase.id).desc()
        ).first()

        top_name = top_supplier.supplier_name if top_supplier else "N/A"

        tab.create_kpi_cards(tab.scrollable_frame, [
            {"title": "Total Proveedores", "value": str(total_suppliers), "color": "#0066cc", "bootstyle": "info"},
            {"title": "Total Comprado", "value": f"${total_purchased:,.2f}", "color": "#28a745", "bootstyle": "success"},
            {"title": "Precio Prom. Unit.", "value": f"${avg_price:,.2f}", "color": "#dc3545", "bootstyle": "danger"},
            {"title": "Proveedor Top", "value": top_name, "color": "#ffc107", "bootstyle": "warning"},
        ])
