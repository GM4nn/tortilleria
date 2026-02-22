"""
StockStatusSection - Niveles de stock actual por insumo
Stock = ultima_compra.remaining + ultima_compra.quantity
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from app.models import Supply, SupplyPurchase, Supplier


class StockStatusSection:
    @staticmethod
    def render(tab, db):
        section = tab.create_section(
            tab.scrollable_frame,
            "📦 Estado de Stock",
            "Niveles de inventario actual por insumo",
            bootstyle="warning"
        )

        supplies = db.query(Supply).all()

        if not supplies:
            tab.create_empty_state(section, "No hay insumos registrados")
            return

        columns = [
            {"text": "Insumo", "stretch": True},
            {"text": "Proveedor", "stretch": True},
            {"text": "Stock Actual", "stretch": False, "width": 120},
            {"text": "Unidad", "stretch": False, "width": 90},
            {"text": "Ultima Compra", "stretch": False, "width": 130},
        ]

        rows = []
        for supply in supplies:
            last_purchase = db.query(SupplyPurchase).filter(
                SupplyPurchase.supply_id == supply.id
            ).order_by(SupplyPurchase.purchase_date.desc()).first()

            if last_purchase:
                current_stock = last_purchase.remaining + last_purchase.quantity
                unit = last_purchase.unit
                d = last_purchase.purchase_date
                last_date = d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)
            else:
                current_stock = 0
                unit = "N/A"
                last_date = "Sin compras"

            rows.append([
                supply.supply_name,
                supply.supplier.supplier_name if supply.supplier else "N/A",
                f"{current_stock:.2f}",
                unit,
                last_date,
            ])

        table_frame = ttk.Frame(section)
        table_frame.pack(fill=BOTH, expand=YES)

        table = Tableview(
            master=table_frame,
            coldata=columns,
            rowdata=rows,
            paginated=False,
            searchable=False,
            bootstyle=WARNING,
            height=min(len(rows), 15),
        )
        table.pack(fill=BOTH, expand=YES)
        table.view.configure(selectmode="none")
