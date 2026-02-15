"""
TopSuppliesSection - Cards de insumo mas/menos comprado (queries corregidas)
"""

from sqlalchemy import func
from app.models import Supply, SupplyPurchase


class TopSuppliesSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "📊 Insumos por Inversion",
            "Comparacion entre el insumo con mayor y menor gasto total",
            bootstyle="warning"
        )

        supplies_summary = db.query(
            Supply.supply_name,
            func.sum(SupplyPurchase.quantity).label('total_quantity'),
            func.sum(SupplyPurchase.total_price).label('total_spent'),
            func.count(SupplyPurchase.id).label('num_purchases')
        ).join(
            Supply, SupplyPurchase.supply_id == Supply.id
        ).group_by(
            Supply.id, Supply.supply_name
        ).order_by(
            func.sum(SupplyPurchase.total_price).desc()
        ).all()

        if not supplies_summary:
            tab.create_empty_state(section, "No hay suficientes insumos para comparar")
            return

        most = supplies_summary[0]
        best = {
            "title": "✅ Insumo Mayor Inversion",
            "name": most.supply_name,
            "details": [
                ("Compras", str(most.num_purchases)),
                ("Cantidad total", f"{most.total_quantity:.2f}"),
                ("Total", f"${most.total_spent:,.2f}")
            ],
            "color": "#28a745"
        }

        worst = None
        if len(supplies_summary) > 1:
            least = supplies_summary[-1]
            worst = {
                "title": "⚠️ Insumo Menor Inversion",
                "name": least.supply_name,
                "details": [
                    ("Compras", str(least.num_purchases)),
                    ("Cantidad total", f"{least.total_quantity:.2f}"),
                    ("Total", f"${least.total_spent:,.2f}")
                ],
                "color": "#dc3545"
            }

        tab.create_highlight_cards(section, best, worst)
