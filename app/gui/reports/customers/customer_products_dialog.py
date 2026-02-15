"""
CustomerProductsDialog - Popup de detalle de productos por cliente
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
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

        canvas = ttk.Canvas(dialog, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side=RIGHT, fill=Y, pady=(0, 20))

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
                # Header
                header = ttk.Frame(scrollable_frame)
                header.pack(fill=X, pady=(0, 10))
                for text, w in [("Producto", 25), ("Cantidad", 15), ("Veces", 10), ("Total", 15)]:
                    ttk.Label(header, text=text, font=("Segoe UI", 10, "bold"), width=w).pack(side=LEFT, padx=5)

                for product in products:
                    row = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1)
                    row.pack(fill=X, pady=2)
                    ttk.Label(row, text=product.name, width=25).pack(side=LEFT, padx=5, pady=5)
                    ttk.Label(row, text=f"{product.quantity:.0f}", width=15).pack(side=LEFT, padx=5, pady=5)
                    ttk.Label(row, text=str(product.times_ordered), width=10).pack(side=LEFT, padx=5, pady=5)
                    ttk.Label(
                        row, text=f"${product.total:,.2f}", width=15,
                        foreground="#28a745", font=("Segoe UI", 10, "bold")
                    ).pack(side=LEFT, padx=5, pady=5)
            else:
                ttk.Label(
                    scrollable_frame, text="No hay productos pedidos por este cliente",
                    foreground="#6c757d", font=("Segoe UI", 11, "italic")
                ).pack(pady=50)

        ttk.Button(dialog, text="Cerrar", bootstyle="secondary", command=dialog.destroy).pack(pady=(0, 20))

        dialog.transient(parent)
        dialog.grab_set()
