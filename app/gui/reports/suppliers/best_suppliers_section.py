"""
BestSuppliersSection - Ranking de proveedores por precio promedio (queries corregidas)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlalchemy import func
from app.models import Supplier, SupplyPurchase
from .supplier_products_dialog import SupplierProductsDialog


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

        # Header
        header_frame = ttk.Frame(section)
        header_frame.pack(fill=X, pady=(0, 5))
        for text, w in [("Proveedor", 22), ("Tipo", 14), ("Precio Prom.", 14), ("Compras", 10), ("Total", 14), ("Acciones", 15)]:
            ttk.Label(header_frame, text=text, font=("Segoe UI", 10, "bold"), width=w).pack(side=LEFT, padx=5)

        for i, s in enumerate(suppliers_data):
            row_frame = ttk.Frame(section)
            row_frame.pack(fill=X, pady=2)

            badge = " ✅ Mas Economico" if i == 0 else ""
            name_color = "#28a745" if i == 0 else "#212529"
            font_weight = "bold" if i == 0 else "normal"

            ttk.Label(row_frame, text=f"{s.supplier_name}{badge}", width=22, font=("Segoe UI", 10, font_weight), foreground=name_color).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=s.product_type or "N/A", width=14).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=f"${s.avg_price:,.2f}", width=14, foreground=name_color).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=str(s.purchases_count), width=10).pack(side=LEFT, padx=5)
            ttk.Label(row_frame, text=f"${s.total_spent:,.2f}", width=14, foreground="#28a745", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=5)

            ttk.Button(
                row_frame, text="👁️ Ver Compras",
                bootstyle="outline-success", width=15,
                command=lambda sid=s.id, sname=s.supplier_name: SupplierProductsDialog.show(tab, sid, sname)
            ).pack(side=LEFT, padx=5)
