"""
SuppliersByDemandSection - Ranking por demanda + cards comparativos
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
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

        columns = [
            {"text": "#", "stretch": False, "width": 50},
            {"text": "Proveedor", "stretch": True},
            {"text": "Tipo", "stretch": False, "width": 130},
            {"text": "Compras", "stretch": False, "width": 90},
            {"text": "Total Comprado", "stretch": False, "width": 140},
        ]

        rows = []
        for i, s in enumerate(suppliers_demand):
            rows.append([
                i + 1,
                s.supplier_name,
                s.product_type or "N/A",
                s.purchases,
                f"${s.total_purchased:,.2f}",
            ])

        table_frame = ttk.Frame(section)
        table_frame.pack(fill=BOTH, expand=YES)

        table = Tableview(
            master=table_frame,
            coldata=columns,
            rowdata=rows,
            paginated=False,
            searchable=False,
            bootstyle=SUCCESS,
            height=min(len(rows), 15),
        )
        table.pack(fill=BOTH, expand=YES)
        table.view.configure(selectmode="none")

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
