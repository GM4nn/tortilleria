"""
Clientes Tab - Customers Reports
- Clientes más fieles
- Venta por cliente con totalidad y productos vendidos
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from sqlalchemy import func
from app.data.database import SessionLocal
from app.models import Sale, SaleDetail, Product, Customer


class CustomersTab(ttk.Frame):
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

    def _on_canvas_configure(self, event):
        """Update the scrollable frame width when canvas is resized"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def refresh_data(self):
        """Refresh all customers data"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Load data from database
        with SessionLocal() as db:
            # Clientes más fieles
            self.create_top_customers_section(db)

            # Separator
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

            # Venta por cliente
            self.create_sales_by_customer_section(db)

    def create_top_customers_section(self, db):
        """Create top customers section (most loyal)"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="🏅 Clientes Más Fieles",
            padding=20,
            bootstyle="info"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Clientes que han comprado más productos por pedidos",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get top customers data (most products ordered)
        top_customers = db.query(
            Customer.id,
            Customer.customer_name,
            func.count(func.distinct(Sale.id)).label('orders'),
            func.sum(SaleDetail.quantity).label('total_products'),
            func.sum(func.distinct(Sale.id) * Sale.total) / func.count(func.distinct(Sale.id)).label('avg_per_sale')
        ).join(
            Sale, Customer.id == Sale.customer_id
        ).join(
            SaleDetail, Sale.id == SaleDetail.sale_id
        ).filter(
            Customer.active == True,
            Customer.active2 == True  # Excluir el cliente Mostrador genérico
        ).group_by(
            Customer.id, Customer.customer_name
        ).order_by(
            func.sum(SaleDetail.quantity).desc()
        ).limit(5).all()

        # Get total spent per customer (separate query to avoid duplication)
        customer_totals = {}
        for customer in top_customers:
            total = db.query(func.sum(Sale.total)).filter(
                Sale.customer_id == customer.id
            ).scalar() or 0
            customer_totals[customer.id] = total

        if top_customers:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Cliente", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Pedidos", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Productos", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total Gastado", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)

            # Table rows
            for i, customer in enumerate(top_customers):
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                # Add trophy icon for top customer
                icon = "🏆" if i == 0 else ""
                customer_name = f"{icon} {customer.customer_name}" if icon else customer.customer_name

                ttk.Label(row_frame, text=customer_name, width=25, font=("Segoe UI", 10, "bold" if i == 0 else "normal")).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=str(customer.orders), width=15).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=f"{customer.total_products:.0f}", width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${customer_totals[customer.id]:,.2f}",
                    width=20,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold" if i == 0 else "normal")
                ).pack(side=LEFT, padx=5)
        else:
            ttk.Label(
                section_frame,
                text="No hay compras registradas de clientes",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def create_sales_by_customer_section(self, db):
        """Create sales by customer section"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="👤 Venta por Cliente",
            padding=20,
            bootstyle="info"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Detalle de ventas con totalidad y productos vendidos (haz clic para ver detalles)",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get customers with sales data
        customer_sales = db.query(
            Customer.id,
            Customer.customer_name,
            func.count(Sale.id).label('orders'),
            func.sum(Sale.total).label('total')
        ).join(
            Sale, Customer.id == Sale.customer_id
        ).filter(
            Customer.active == True,
            Customer.active2 == True  # Excluir el cliente Mostrador genérico
        ).group_by(
            Customer.id, Customer.customer_name
        ).order_by(
            func.sum(Sale.total).desc()
        ).all()

        if customer_sales:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Cliente", font=("Segoe UI", 10, "bold"), width=30).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Pedidos", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Acciones", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)

            # Table rows
            for customer in customer_sales:
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                ttk.Label(row_frame, text=customer.customer_name, width=30).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=str(customer.orders), width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${customer.total:,.2f}",
                    width=20,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5)

                # Ver Productos button
                btn = ttk.Button(
                    row_frame,
                    text="📋 Ver Productos",
                    bootstyle="outline-info",
                    width=15,
                    command=lambda c_id=customer.id, c_name=customer.customer_name: self.show_customer_products(c_id, c_name, db)
                )
                btn.pack(side=LEFT, padx=5)

        else:
            ttk.Label(
                section_frame,
                text="No hay compras registradas de clientes",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def show_customer_products(self, customer_id, customer_name, db):
        """Show customer products in a dialog"""
        # Create dialog window
        dialog = ttk.Toplevel(self)
        dialog.title(f"Productos de {customer_name}")
        dialog.geometry("700x500")

        # Title
        ttk.Label(
            dialog,
            text=f"Productos comprados por {customer_name}",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20, padx=20)

        # Create scrollable frame
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

        # Get products purchased by this customer
        products = db.query(
            Product.name,
            func.sum(SaleDetail.quantity).label('quantity'),
            func.count(SaleDetail.id).label('times_purchased'),
            func.sum(SaleDetail.subtotal).label('total')
        ).join(
            SaleDetail, Product.id == SaleDetail.product_id
        ).join(
            Sale, SaleDetail.sale_id == Sale.id
        ).filter(
            Sale.customer_id == customer_id
        ).group_by(
            Product.id, Product.name
        ).order_by(
            func.sum(SaleDetail.quantity).desc()
        ).all()

        if products:
            # Table header
            header_frame = ttk.Frame(scrollable_frame)
            header_frame.pack(fill=X, pady=(0, 10))

            ttk.Label(header_frame, text="Producto", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Cantidad", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Veces", font=("Segoe UI", 10, "bold"), width=10).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)

            # Table rows
            for product in products:
                row_frame = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1)
                row_frame.pack(fill=X, pady=2)

                ttk.Label(row_frame, text=product.name, width=25).pack(side=LEFT, padx=5, pady=5)
                ttk.Label(row_frame, text=f"{product.quantity:.0f}", width=15).pack(side=LEFT, padx=5, pady=5)
                ttk.Label(row_frame, text=str(product.times_purchased), width=10).pack(side=LEFT, padx=5, pady=5)
                ttk.Label(
                    row_frame,
                    text=f"${product.total:,.2f}",
                    width=15,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5, pady=5)

        else:
            ttk.Label(
                scrollable_frame,
                text="No hay productos comprados por este cliente",
                foreground="#6c757d",
                font=("Segoe UI", 11, "italic")
            ).pack(pady=50)

        # Close button
        ttk.Button(
            dialog,
            text="Cerrar",
            bootstyle="secondary",
            command=dialog.destroy
        ).pack(pady=(0, 20))

        # Center dialog
        dialog.transient(self)
        dialog.grab_set()
