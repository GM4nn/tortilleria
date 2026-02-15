"""
SupplierProductsDialog - Popup de compras por proveedor (queries corregidas)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.data.database import SessionLocal
from app.models import Supply, SupplyPurchase


class SupplierProductsDialog:
    @staticmethod
    def show(parent, supplier_id, supplier_name):
        dialog = ttk.Toplevel(parent)
        dialog.title(f"Compras a {supplier_name}")
        dialog.geometry("750x500")

        title_frame = ttk.Frame(dialog, padding=20)
        title_frame.pack(fill=X)
        ttk.Label(
            title_frame, text=f"Historial de compras a {supplier_name}",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=W)

        products_frame = ttk.Frame(dialog, padding=(20, 0, 20, 20))
        products_frame.pack(fill=BOTH, expand=True)

        with SessionLocal() as db:
            purchases = db.query(
                Supply.supply_name,
                SupplyPurchase.purchase_date,
                SupplyPurchase.quantity,
                SupplyPurchase.unit,
                SupplyPurchase.unit_price,
                SupplyPurchase.total_price
            ).join(
                Supply, SupplyPurchase.supply_id == Supply.id
            ).filter(
                SupplyPurchase.supplier_id == supplier_id
            ).order_by(
                SupplyPurchase.purchase_date.desc()
            ).all()

            if purchases:
                canvas = ttk.Canvas(products_frame, highlightthickness=0)
                scrollbar = ttk.Scrollbar(products_frame, orient=VERTICAL, command=canvas.yview)
                scrollable = ttk.Frame(canvas)

                scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                canvas.create_window((0, 0), window=scrollable, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side=LEFT, fill=BOTH, expand=True)
                scrollbar.pack(side=RIGHT, fill=Y)

                header = ttk.Frame(scrollable)
                header.pack(fill=X, pady=(0, 10))
                for text, w in [("Insumo", 18), ("Fecha", 12), ("Cantidad", 12), ("Unidad", 10), ("Precio Unit.", 12), ("Total", 12)]:
                    ttk.Label(header, text=text, font=("Segoe UI", 10, "bold"), width=w).pack(side=LEFT, padx=5)

                for p in purchases:
                    row = ttk.Frame(scrollable)
                    row.pack(fill=X, pady=2)

                    date_str = p.purchase_date.strftime("%Y-%m-%d") if hasattr(p.purchase_date, 'strftime') else str(p.purchase_date)

                    ttk.Label(row, text=p.supply_name, width=18).pack(side=LEFT, padx=5)
                    ttk.Label(row, text=date_str, width=12).pack(side=LEFT, padx=5)
                    ttk.Label(row, text=f"{p.quantity:.2f}", width=12).pack(side=LEFT, padx=5)
                    ttk.Label(row, text=p.unit, width=10).pack(side=LEFT, padx=5)
                    ttk.Label(row, text=f"${p.unit_price:,.2f}", width=12).pack(side=LEFT, padx=5)
                    ttk.Label(row, text=f"${p.total_price:,.2f}", width=12, foreground="#28a745", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=5)
            else:
                ttk.Label(
                    products_frame, text="Este proveedor no tiene compras registradas",
                    font=("Segoe UI", 11, "italic"), foreground="#6c757d"
                ).pack(expand=True)

        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill=X)
        ttk.Button(button_frame, text="Cerrar", bootstyle="secondary", command=dialog.destroy, width=15).pack(side=RIGHT)

        dialog.transient(parent)
        dialog.grab_set()
