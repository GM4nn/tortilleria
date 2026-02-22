"""
SupplierProductsDialog - Popup de compras por proveedor (queries corregidas)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
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
                columns = [
                    {"text": "Insumo", "stretch": True},
                    {"text": "Fecha", "stretch": False, "width": 100},
                    {"text": "Cantidad", "stretch": False, "width": 90},
                    {"text": "Unidad", "stretch": False, "width": 80},
                    {"text": "Precio Unit.", "stretch": False, "width": 110},
                    {"text": "Total", "stretch": False, "width": 110},
                ]

                rows = []
                for p in purchases:
                    date_str = p.purchase_date.strftime("%Y-%m-%d") if hasattr(p.purchase_date, 'strftime') else str(p.purchase_date)
                    rows.append([
                        p.supply_name,
                        date_str,
                        f"{p.quantity:.2f}",
                        p.unit,
                        f"${p.unit_price:,.2f}",
                        f"${p.total_price:,.2f}",
                    ])

                table = Tableview(
                    master=products_frame,
                    coldata=columns,
                    rowdata=rows,
                    paginated=False,
                    searchable=False,
                    bootstyle=SUCCESS,
                    height=min(len(rows), 18),
                )
                table.pack(fill=BOTH, expand=YES)
                table.view.configure(selectmode="none")
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
