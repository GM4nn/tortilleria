"""
Insumos Tab - Supplies Reports
- Compras totales
- Listado de insumos con totalidad específica y proveedor
- Insumo más comprado
- Insumo menos comprado
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sqlalchemy import func
from app.data.database import SessionLocal
from app.models import Supply, Supplier


class SuppliesTab(ttk.Frame):
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
        """Refresh all supplies data"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Load data from database
        with SessionLocal() as db:
            # Compras Totales
            self.create_total_purchases_section(db)

            # Separator
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

            # Listado de Insumos
            self.create_supplies_list_section(db)

            # Separator
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).pack(fill=X, pady=20, padx=20)

            # Insumo más/menos comprado
            self.create_top_supplies_section(db)

    def create_total_purchases_section(self, db):
        """Create total purchases summary section"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="💰 Compras Totales de Insumos",
            padding=20,
            bootstyle="warning"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Resumen general de compras de insumos",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get total purchases data
        total_data = db.query(
            func.sum(Supply.total_price).label('total_invested'),
            func.count(Supply.id).label('items_purchased'),
            func.count(func.distinct(Supply.supplier_id)).label('suppliers')
        ).first()

        # Create stats cards
        stats_frame = ttk.Frame(section_frame)
        stats_frame.pack(fill=X)

        # Total Invested Card
        card1 = ttk.Frame(stats_frame, bootstyle="info")
        card1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        ttk.Label(
            card1,
            text="Total Invertido",
            font=("Segoe UI", 11),
            foreground="#6c757d"
        ).pack(pady=(10, 5))

        total_invested = total_data.total_invested if total_data.total_invested else 0
        ttk.Label(
            card1,
            text=f"${total_invested:,.2f}",
            font=("Segoe UI", 20, "bold"),
            foreground="#0066cc"
        ).pack(pady=(0, 10))

        # Items Purchased Card
        card2 = ttk.Frame(stats_frame, bootstyle="success")
        card2.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        ttk.Label(
            card2,
            text="Ítems Comprados",
            font=("Segoe UI", 11),
            foreground="#6c757d"
        ).pack(pady=(10, 5))

        items_purchased = total_data.items_purchased if total_data.items_purchased else 0
        ttk.Label(
            card2,
            text=str(items_purchased),
            font=("Segoe UI", 20, "bold"),
            foreground="#28a745"
        ).pack(pady=(0, 10))

        # Suppliers Card
        card3 = ttk.Frame(stats_frame, bootstyle="warning")
        card3.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

        ttk.Label(
            card3,
            text="Proveedores",
            font=("Segoe UI", 11),
            foreground="#6c757d"
        ).pack(pady=(10, 5))

        suppliers_count = total_data.suppliers if total_data.suppliers else 0
        ttk.Label(
            card3,
            text=str(suppliers_count),
            font=("Segoe UI", 20, "bold"),
            foreground="#ffc107"
        ).pack(pady=(0, 10))

    def create_supplies_list_section(self, db):
        """Create supplies list section"""
        section_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="📋 Listado de Insumos",
            padding=20,
            bootstyle="warning"
        )
        section_frame.pack(fill=X, padx=20, pady=10)

        subtitle = ttk.Label(
            section_frame,
            text="Insumos con su totalidad específica y proveedor",
            font=("Segoe UI", 10),
            foreground="#6c757d"
        )
        subtitle.pack(anchor=W, pady=(0, 15))

        # Get supplies with supplier info
        supplies = db.query(
            Supply,
            Supplier.supplier_name
        ).join(
            Supplier, Supply.supplier_id == Supplier.id
        ).order_by(
            Supply.total_price.desc()
        ).all()

        if supplies:
            # Table header
            header_frame = ttk.Frame(section_frame)
            header_frame.pack(fill=X, pady=(0, 5))

            ttk.Label(header_frame, text="Insumo", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Proveedor", font=("Segoe UI", 10, "bold"), width=25).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Cantidad", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)
            ttk.Label(header_frame, text="Total", font=("Segoe UI", 10, "bold"), width=15).pack(side=LEFT, padx=5)

            # Table rows
            for supply, supplier_name in supplies:
                row_frame = ttk.Frame(section_frame)
                row_frame.pack(fill=X, pady=2)

                ttk.Label(row_frame, text=supply.supply_name, width=25).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=supplier_name, width=25).pack(side=LEFT, padx=5)
                ttk.Label(row_frame, text=f"{supply.quantity:.2f} {supply.unit}", width=15).pack(side=LEFT, padx=5)
                ttk.Label(
                    row_frame,
                    text=f"${supply.total_price:,.2f}",
                    width=15,
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                ).pack(side=LEFT, padx=5)
        else:
            ttk.Label(
                section_frame,
                text="No hay insumos registrados",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)

    def create_top_supplies_section(self, db):
        """Create most and least purchased supplies section"""
        section_frame = ttk.Frame(self.scrollable_frame)
        section_frame.pack(fill=X, padx=20, pady=10)

        # Get supplies grouped by name with totals
        supplies_summary = db.query(
            Supply.supply_name,
            Supplier.supplier_name,
            func.sum(Supply.quantity).label('total_quantity'),
            func.sum(Supply.total_price).label('total_spent')
        ).join(
            Supplier, Supply.supplier_id == Supplier.id
        ).group_by(
            Supply.supply_name,
            Supplier.supplier_name
        ).order_by(
            func.sum(Supply.total_price).desc()
        ).all()

        if len(supplies_summary) > 0:
            cards_frame = ttk.Frame(section_frame)
            cards_frame.pack(fill=X)

            # Most purchased supply
            most_purchased = supplies_summary[0]
            most_card = ttk.Labelframe(
                cards_frame,
                text="✅ Insumo Más Comprado",
                padding=15,
                bootstyle="success"
            )
            most_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

            ttk.Label(
                most_card,
                text=most_purchased.supply_name,
                font=("Segoe UI", 14, "bold"),
                foreground="#28a745"
            ).pack(anchor=W)

            ttk.Label(
                most_card,
                text=f"Proveedor: {most_purchased.supplier_name}",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=(5, 0))

            ttk.Label(
                most_card,
                text=f"Cantidad: {most_purchased.total_quantity:.2f}",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=(2, 0))

            ttk.Label(
                most_card,
                text=f"Total: ${most_purchased.total_spent:,.2f}",
                font=("Segoe UI", 12, "bold"),
                foreground="#28a745"
            ).pack(anchor=W, pady=(5, 0))

            # Least purchased supply
            if len(supplies_summary) > 1:
                least_purchased = supplies_summary[-1]
                least_card = ttk.Labelframe(
                    cards_frame,
                    text="⚠️ Insumo Menos Comprado",
                    padding=15,
                    bootstyle="danger"
                )
                least_card.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

                ttk.Label(
                    least_card,
                    text=least_purchased.supply_name,
                    font=("Segoe UI", 14, "bold"),
                    foreground="#dc3545"
                ).pack(anchor=W)

                ttk.Label(
                    least_card,
                    text=f"Proveedor: {least_purchased.supplier_name}",
                    font=("Segoe UI", 10)
                ).pack(anchor=W, pady=(5, 0))

                ttk.Label(
                    least_card,
                    text=f"Cantidad: {least_purchased.total_quantity:.2f}",
                    font=("Segoe UI", 10)
                ).pack(anchor=W, pady=(2, 0))

                ttk.Label(
                    least_card,
                    text=f"Total: ${least_purchased.total_spent:,.2f}",
                    font=("Segoe UI", 12, "bold"),
                    foreground="#dc3545"
                ).pack(anchor=W, pady=(5, 0))
        else:
            ttk.Label(
                section_frame,
                text="No hay suficientes insumos para comparar",
                foreground="#6c757d",
                font=("Segoe UI", 10, "italic")
            ).pack(pady=10)
