"""
StockStatusSection - Niveles de stock actual por insumo
Replica la logica de SupplyProvider._calculate_current_stock()
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from sqlalchemy import func
from app.models import Supply, SupplyPurchase, SupplyConsumption, Supplier


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
            # Calculate current stock (same logic as SupplyProvider._calculate_current_stock)
            last_consumption = db.query(SupplyConsumption).filter(
                SupplyConsumption.supply_id == supply.id
            ).order_by(SupplyConsumption.end_date.desc()).first()

            if last_consumption:
                current_stock = last_consumption.quantity_remaining
                unit = last_consumption.unit
            else:
                total_purchased = db.query(
                    func.coalesce(func.sum(SupplyPurchase.quantity), 0)
                ).filter(SupplyPurchase.supply_id == supply.id).scalar() or 0
                current_stock = total_purchased

                # Get unit from last purchase
                last_purchase_for_unit = db.query(SupplyPurchase.unit).filter(
                    SupplyPurchase.supply_id == supply.id
                ).order_by(SupplyPurchase.purchase_date.desc()).first()
                unit = last_purchase_for_unit.unit if last_purchase_for_unit else "N/A"

            # Get last purchase date
            last_purchase = db.query(SupplyPurchase.purchase_date).filter(
                SupplyPurchase.supply_id == supply.id
            ).order_by(SupplyPurchase.purchase_date.desc()).first()

            last_date = "Sin compras"
            if last_purchase:
                d = last_purchase.purchase_date
                last_date = d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)

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
