"""
BestSuppliersSection - Ranking de proveedores por precio promedio (queries corregidas)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from sqlalchemy import func
from app.models import Supplier, SupplyPurchase


class BestSuppliersSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "⭐ Mejores Proveedores",
            "Ordenados del mas economico al mas caro por precio promedio unitario",
            bootstyle="success"
        )

        suppliers_data = db.query(
            Supplier.id,
            Supplier.supplier_name,
            Supplier.product_type,
            func.avg(SupplyPurchase.unit_price).label('avg_price'),
            func.count(SupplyPurchase.id).label('purchases_count'),
            func.coalesce(func.sum(SupplyPurchase.total_price), 0).label('total_spent')
        ).join(
            SupplyPurchase, Supplier.id == SupplyPurchase.supplier_id
        ).group_by(
            Supplier.id, Supplier.supplier_name, Supplier.product_type
        ).order_by(
            func.avg(SupplyPurchase.unit_price).asc()
        ).all()

        if not suppliers_data:
            tab.create_empty_state(section, "No hay proveedores con compras registradas")
            return

        columns = [
            {"text": "#", "stretch": False, "width": 50},
            {"text": "Proveedor", "stretch": True},
            {"text": "Tipo", "stretch": False, "width": 130},
            {"text": "Precio Prom.", "stretch": False, "width": 120},
            {"text": "Compras", "stretch": False, "width": 90},
            {"text": "Total Gastado", "stretch": False, "width": 130},
        ]

        rows = []
        for i, s in enumerate(suppliers_data):
            badge = " (Mas Economico)" if i == 0 else ""
            rows.append([
                i + 1,
                f"{s.supplier_name}{badge}",
                s.product_type or "N/A",
                f"${s.avg_price:,.2f}",
                s.purchases_count,
                f"${s.total_spent:,.2f}",
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
