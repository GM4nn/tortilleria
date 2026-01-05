"""
Proveedores Tab - Suppliers Reports
- Mejores proveedores (del más caro al más económico)
- Proveedor más solicitado
- Proveedor menos solicitado
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlalchemy import func
from app.data.database import SessionLocal
from app.models import Supply, Supplier


class SuppliersTab(ttk.Frame):
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
        """Refresh all suppliers data"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Load data from database
        with SessionLocal() as db:
            # Mejores Proveedores
            self.create_best_suppliers_section(db)

            # Separator
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

            # Proveedores por Demanda
            self.create_suppliers_by_demand_section(db)

            # Separator
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

            # Proveedor más/menos solicitado
            self.create_top_suppliers_section(db)

    def create_best_suppliers_section(self, db):
        """Create best suppliers section (sorted by price)"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="⭐ Mejores Proveedores",
            padding=20,
            bootstyle="success"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Ordenados del más económico al más caro (haz clic para ver productos)",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get suppliers with average price and rating simulation
        suppliers_data = db.query(
            Supplier.id,
            Supplier.supplier_name,
            func.avg(Supply.unit_price).label('avg_price'),
            func.count(Supply.id).label('products_count')
        ).join(
            Supply, Supplier.id == Supply.supplier_id
        ).group_by(
            Supplier.id,
            Supplier.supplier_name
        ).order_by(
            func.avg(Supply.unit_price).asc()  # From cheapest to most expensive
        ).all()

        if suppliers_data:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Proveedor", font=("Segoe UI", 10, "bold"), width=30).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Precio Promedio", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Rating", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Acciones", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)

            # Table rows
            for i, supplier_data in enumerate(suppliers_data):
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                # Add badge for most economical
                badge = "✅ Más Económico" if i == 0 else ""
                supplier_name = f"{supplier_data.supplier_name} {badge}" if badge else supplier_data.supplier_name

                ttk.Label(
                    row_frame,
                    text=supplier_name,
                    width=30,
                    font=("Segoe UI", 10, "bold" if i == 0 else "normal"),
                    foreground="#28a745" if i == 0 else "#212529"
                ).pack(side=LEFT, padx=5)

                ttk.Label(
                    row_frame,
                    text=f"${supplier_data.avg_price:,.2f}",
                    width=20,
                    foreground="#28a745" if i == 0 else "#212529"
                ).pack(side=LEFT, padx=5)

                # Simulate rating (higher for cheaper suppliers)
                rating = 5.0 - (i * 0.2) if i < 5 else 4.0
                ttk.Label(
                    row_frame,
                    text=f"⭐ {rating:.1f}",
                    width=15,
                    foreground="#ffc107"
                ).pack(side=LEFT, padx=5)

                # Ver Productos button
                btn = ttk.Button(
                    row_frame,
                    text="👁️ Ver Productos",
                    bootstyle="outline-success",
                    width=15,
                    command=lambda sid=supplier_data.id, sname=supplier_data.supplier_name: self.show_supplier_products(sid, sname, db)
                )
                btn.pack(side=LEFT, padx=5)
        else:
            ttk.Label(
                section_frame,
                text="No hay proveedores con productos registrados",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def create_suppliers_by_demand_section(self, db):
        """Create suppliers by demand section"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="📊 Proveedores por Demanda",
            padding=20,
            bootstyle="success"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Ranking de proveedores según pedidos realizados",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get suppliers by number of orders
        suppliers_demand = db.query(
            Supplier.supplier_name,
            func.count(Supply.id).label('orders'),
            func.sum(Supply.total_price).label('total_purchased')
        ).join(
            Supply, Supplier.id == Supply.supplier_id
        ).group_by(
            Supplier.supplier_name
        ).order_by(
            func.count(Supply.id).desc()
        ).all()

        if suppliers_demand:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Proveedor", font=("Segoe UI", 10, "bold"), width=30).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Pedidos", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total Comprado", font=("Segoe UI", 10, "bold"), width=20).pack(side=LEFT, padx=5)

            # Table rows
            for supplier in suppliers_demand:
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                ttk.Label(row_frame, text=supplier.supplier_name, width=30).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=str(supplier.orders), width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${supplier.total_purchased:,.2f}",
                    width=20,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5)
        else:
            ttk.Label(
                section_frame,
                text="No hay datos de proveedores",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def create_top_suppliers_section(self, db):
        """Create most and least requested suppliers section"""
        section_frame = ttk.Frame(self.scrollable_frame)
        section_frame.pack(fill=X, padx=20, pady=10)

        # Get suppliers by demand
        suppliers_by_demand = db.query(
            Supplier.supplier_name,
            func.count(Supply.id).label('orders'),
            func.sum(Supply.total_price).label('total')
        ).join(
            Supply, Supplier.id == Supply.supplier_id
        ).group_by(
            Supplier.supplier_name
        ).order_by(
            func.count(Supply.id).desc()
        ).all()

        if len(suppliers_by_demand) > 0:
            cards_frame = ttk.Frame(section_frame)
            cards_frame.pack(fill=X)

            # Most requested supplier
            most_requested = suppliers_by_demand[0]
            most_card = ttk.Labelframe(
                cards_frame,
                text="✅ Proveedor Más Solicitado",
                padding=15,
                bootstyle="success"
            )
            most_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

            ttk.Label(
                most_card,
                text=most_requested.supplier_name,
                font=("Segoe UI", 14, "bold"),
                foreground="#28a745"
            ).pack(anchor=W)

            ttk.Label(
                most_card,
                text=f"Pedidos: {most_requested.orders}",
                font=("Segoe UI", 11)
            ).pack(anchor=W, pady=(5, 0))

            ttk.Label(
                most_card,
                text=f"Total: ${most_requested.total:,.2f}",
                font=("Segoe UI", 12, "bold"),
                foreground="#28a745"
            ).pack(anchor=W, pady=(5, 0))

            # Least requested supplier
            if len(suppliers_by_demand) > 1:
                least_requested = suppliers_by_demand[-1]
                least_card = ttk.Labelframe(
                    cards_frame,
                    text="⚠️ Proveedor Menos Solicitado",
                    padding=15,
                    bootstyle="danger"
                )
                least_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

                ttk.Label(
                    least_card,
                    text=least_requested.supplier_name,
                    font=("Segoe UI", 14, "bold"),
                    foreground="#dc3545"
                ).pack(anchor=W)

                ttk.Label(
                    least_card,
                    text=f"Pedidos: {least_requested.orders}",
                    font=("Segoe UI", 11)
                ).pack(anchor=W, pady=(5, 0))

                ttk.Label(
                    least_card,
                    text=f"Total: ${least_requested.total:,.2f}",
                    font=("Segoe UI", 12, "bold"),
                    foreground="#dc3545"
                ).pack(anchor=W, pady=(5, 0))
        else:
            ttk.Label(
                section_frame,
                text="No hay suficientes proveedores para comparar",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def show_supplier_products(self, supplier_id, supplier_name, db):
        """Show supplier products in a dialog without leaving the main screen"""
        # Create dialog window
        dialog = ttk.Toplevel(self)
        dialog.title(f"Productos de {supplier_name}")
        dialog.geometry("700x500")

        # Title
        title_frame = ttk.Frame(dialog, padding=20)
        title_frame.pack(fill=X)

        ttk.Label(
            title_frame,
            text=f"Productos de {supplier_name}",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor=W)

        # Products list
        products_frame = ttk.Frame(dialog, padding=(20, 0, 20, 20))
        products_frame.pack(fill=BOTH, expand=True)

        # Get products from this supplier
        products = db.query(Supply).filter(Supply.supplier_id == supplier_id).all()

        if products:
            # Create scrollable frame for products
            canvas = ttk.Canvas(products_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(products_frame, orient=VERTICAL, command=canvas.yview)
            scrollable = ttk.Frame(canvas)

            scrollable.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            scrollbar.pack(side=RIGHT, fill=Y)

            # Table header
            header_frame = ttk.Frame(scrollable)
            header_frame.pack(fill=X, pady=(0, 10))

            ttk.Label(header_frame, text="Producto", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Cantidad", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Precio Unit.", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)

            # Product rows
            for product in products:
                row_frame = ttk.Frame(scrollable)
                row_frame.pack(fill=X, pady=2)

                ttk.Label(row_frame, text=product.supply_name, width=25).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=f"{product.quantity:.2f} {product.unit}", width=15).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=f"${product.unit_price:,.2f}", width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${product.total_price:,.2f}",
                    width=15,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5)
        else:
            ttk.Label(
                products_frame,
                text="Este proveedor no tiene productos registrados",
                font=("Segoe UI", 11, "italic"),
                foreground="#6c757d"
            ).pack(expand=True)

        # Close button
        button_frame = ttk.Frame(dialog, padding=20)
        button_frame.pack(fill=X)

        ttk.Button(
            button_frame,
            text="Cerrar",
            bootstyle="secondary",
            command=dialog.destroy,
            width=15
        ).pack(side=RIGHT)

        # Center dialog
        dialog.transient(self)
        dialog.grab_set()
