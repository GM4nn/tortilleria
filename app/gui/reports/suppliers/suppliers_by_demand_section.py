"""
SuppliersByDemandSection - Ranking por demanda + cards comparativos
"""

from sqlalchemy import func
from app.models import Supplier, SupplyPurchase


class SuppliersByDemandSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "📊 Proveedores por Demanda",
            "Ranking de proveedores segun cantidad de compras realizadas",
            bootstyle="success"
        )

        suppliers_demand = db.query(
            Supplier.supplier_name,
            Supplier.product_type,
            func.count(SupplyPurchase.id).label('purchases'),
            func.coalesce(func.sum(SupplyPurchase.total_price), 0).label('total_purchased')
        ).join(
            SupplyPurchase, Supplier.id == SupplyPurchase.supplier_id
        ).group_by(
            Supplier.id, Supplier.supplier_name, Supplier.product_type
        ).order_by(
            func.count(SupplyPurchase.id).desc()
        ).all()

        if not suppliers_demand:
            tab.create_empty_state(section, "No hay datos de proveedores")
            return

        headers = [("Proveedor", 22), ("Tipo", 14), ("Compras", 12), ("Total Comprado", 18)]
        rows = []
        for s in suppliers_demand:
            rows.append([
                s.supplier_name,
                s.product_type or "N/A",
                str(s.purchases),
                f"${s.total_purchased:,.2f}"
            ])

        tab.create_table(section, headers, rows, money_cols={3})

        # Highlight cards
        most = suppliers_demand[0]
        best = {
            "title": "✅ Proveedor Mas Solicitado",
            "name": most.supplier_name,
            "details": [("Compras", str(most.purchases)), ("Total", f"${most.total_purchased:,.2f}")],
            "color": "#28a745"
        }

        worst = None
        if len(suppliers_demand) > 1:
            least = suppliers_demand[-1]
            worst = {
                "title": "⚠️ Proveedor Menos Solicitado",
                "name": least.supplier_name,
                "details": [("Compras", str(least.purchases)), ("Total", f"${least.total_purchased:,.2f}")],
                "color": "#dc3545"
            }

        tab.create_highlight_cards(section, best, worst)
