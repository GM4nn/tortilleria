"""
StockStatusSection - Niveles de stock actual por insumo
Replica la logica de SupplyProvider._calculate_current_stock()
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
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

        # Header
        header_frame = ttk.Frame(section)
        header_frame.pack(fill=X, pady=(0, 5))
        for text, w in [("Insumo", 18), ("Proveedor", 18), ("Stock Actual", 14), ("Unidad", 10), ("Ultima Compra", 14)]:
            ttk.Label(header_frame, text=text, font=("Segoe UI", 10, "bold"), width=w).pack(side=LEFT, padx=5)

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

            # Color based on stock level
            if current_stock <= 0:
                color = "#dc3545"  # Red
            elif current_stock < 10:
                color = "#ffc107"  # Yellow
            else:
                color = "#28a745"  # Green

            row_frame = ttk.Frame(section)
            row_frame.pack(fill=X, pady=2)

            ttk.Label(row_frame, text=supply.supply_name, width=18).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=supply.supplier.supplier_name if supply.supplier else "N/A", width=18).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=f"{current_stock:.2f}", width=14, foreground=color, font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=unit, width=10).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=last_date, width=14).pack(side=LEFT, padx=5)
