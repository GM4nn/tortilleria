"""
Ventas Tab - Sales Reports
- Ventas por fecha
- Ventas por producto (más vendido, menos vendido)
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.data.database import SessionLocal
from app.models import Sale, SaleDetail, Product


class SalesTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # Create scrollable frame
        self.canvas = ttk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Bind to canvas resize to update scrollable frame width
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Content will be loaded in refresh_data()

    def _on_canvas_configure(self, event):
        """Update the scrollable frame width when canvas is resized"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def refresh_data(self):
        """Refresh all sales data"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Load data from database
        with SessionLocal() as db:
            # Ventas por Fecha (últimos 5 días)
            self.create_sales_by_date_section(db)

            # Separator
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

            # Ventas por Producto
            self.create_sales_by_product_section(db)

    def create_sales_by_date_section(self, db):
        """Create sales by date section"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="📅 Ventas por Fecha",
            padding=20,
            bootstyle="primary"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Resumen de ventas diarias de los últimos 5 días",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get sales data for last 5 days
        today = datetime.now().date()
        five_days_ago = today - timedelta(days=4)

        sales_by_date = db.query(
            func.date(Sale.date).label('date'),
            func.count(Sale.id).label('orders'),
            func.sum(Sale.total).label('total')
        ).filter(
            func.date(Sale.date) >= five_days_ago
        ).group_by(
            func.date(Sale.date)
        ).order_by(
            func.date(Sale.date).desc()
        ).all()

        # Create table
        if sales_by_date:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Fecha", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Pedidos", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total Vendido", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)

            # Table rows
            for sale in sales_by_date:
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                date_str = sale.date.strftime("%Y-%m-%d") if hasattr(sale.date, 'strftime') else str(sale.date)

                ttk.Label(row_frame, text=date_str, width=15).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=str(sale.orders), width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${sale.total:,.2f}",
                    width=20,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5)
        else:
            ttk.Label(
                section_frame,
                text="No hay ventas registradas en los últimos 5 días",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def create_sales_by_product_section(self, db):
        """Create sales by product section"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="🏆 Ventas por Producto",
            padding=20,
            bootstyle="primary"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Análisis detallado de productos vendidos",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get product sales data
        product_sales = db.query(
            Product.name,
            func.sum(SaleDetail.quantity).label('quantity'),
            func.count(SaleDetail.id).label('sales_count'),
            func.sum(SaleDetail.subtotal).label('total')
        ).join(
            SaleDetail, Product.id == SaleDetail.product_id
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.sum(SaleDetail.subtotal).desc()
        ).all()

        if product_sales:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Producto", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Cantidad", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Ventas", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)

            # Table rows
            for product in product_sales:
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                ttk.Label(row_frame, text=product.name, width=20).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=f"{product.quantity:.0f}", width=15).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=str(product.sales_count), width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${product.total:,.2f}",
                    width=20,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5)

            # Highlight cards for most and least sold products
            cards_frame = ttk.Frame(section_frame)
            cards_frame.pack(fill=X, pady=(20, 0))

            # Most sold product
            most_sold = product_sales[0]
            most_card = ttk.Labelframe(
                cards_frame,
                text="✅ Producto Más Vendido",
                padding=15,
                bootstyle="success"
            )
            most_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

            ttk.Label(
                most_card,
                text=most_sold.name,
                font=("Segoe UI", 14, "bold"),
                foreground="#28a745"
            ).pack(anchor=W)

            ttk.Label(
                most_card,
                text=f"Cantidad: {most_sold.quantity:.0f}",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=(5, 0))

            ttk.Label(
                most_card,
                text=f"Total: ${most_sold.total:,.2f}",
                font=("Segoe UI", 12, "bold"),
                foreground="#28a745"
            ).pack(anchor=W, pady=(5, 0))

            # Least sold product
            least_sold = product_sales[-1]
            least_card = ttk.Labelframe(
                cards_frame,
                text="⚠️ Producto Menos Vendido",
                padding=15,
                bootstyle="danger"
            )
            least_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

            ttk.Label(
                least_card,
                text=least_sold.name,
                font=("Segoe UI", 14, "bold"),
                foreground="#dc3545"
            ).pack(anchor=W)

            ttk.Label(
                least_card,
                text=f"Cantidad: {least_sold.quantity:.0f}",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=(5, 0))

            ttk.Label(
                least_card,
                text=f"Total: ${least_sold.total:,.2f}",
                font=("Segoe UI", 12, "bold"),
                foreground="#dc3545"
            ).pack(anchor=W, pady=(5, 0))
        else:
            ttk.Label(
                section_frame,
                text="No hay ventas de productos registradas",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)
