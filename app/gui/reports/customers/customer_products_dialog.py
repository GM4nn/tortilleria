"""
CustomerProductsDialog - Popup de detalle de productos por cliente
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from sqlalchemy import func
from app.data.database import SessionLocal
from app.models import Product, Order, OrderDetail


class CustomerProductsDialog:
    @staticmethod
    def show(parent, customer_id, customer_name):
        dialog = ttk.Toplevel(parent)
        dialog.title(f"Productos de {customer_name}")
        dialog.geometry("700x500")

        ttk.Label(
            dialog, text=f"Productos pedidos por {customer_name}",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20, padx=20)

        products_frame = ttk.Frame(dialog, padding=(20, 0, 20, 20))
        products_frame.pack(fill=BOTH, expand=True)

        with SessionLocal() as db:
            products = db.query(
                Product.name,
                func.sum(OrderDetail.quantity).label('quantity'),
                func.count(OrderDetail.id).label('times_ordered'),
                func.sum(OrderDetail.subtotal).label('total')
            ).join(
                OrderDetail, Product.id == OrderDetail.product_id
            ).join(
                Order, OrderDetail.order_id == Order.id
            ).filter(
                Order.customer_id == customer_id
            ).group_by(
                Product.id, Product.name
            ).order_by(
                func.sum(OrderDetail.quantity).desc()
            ).all()

            if products:
                columns = [
                    {"text": "Producto", "stretch": True},
                    {"text": "Cantidad", "stretch": False, "width": 100},
                    {"text": "Veces", "stretch": False, "width": 80},
                    {"text": "Total", "stretch": False, "width": 120},
                ]

                rows = []
                for product in products:
                    rows.append([
                        product.name,
                        f"{product.quantity:.0f}",
                        product.times_ordered,
                        f"${product.total:,.2f}",
                    ])

                table = Tableview(
                    master=products_frame,
                    coldata=columns,
                    rowdata=rows,
                    paginated=False,
                    searchable=False,
                    bootstyle=INFO,
                    height=min(len(rows), 18),
                )
                table.pack(fill=BOTH, expand=YES)
                table.view.configure(selectmode="none")
            else:
                ttk.Label(
                    products_frame, text="No hay productos pedidos por este cliente",
                    foreground="#6c757d", font=("Segoe UI", 11, "italic")
                ).pack(pady=50)

        ttk.Button(dialog, text="Cerrar", bootstyle="secondary", command=dialog.destroy).pack(pady=(0, 20))

        dialog.transient(parent)
        dialog.grab_set()
