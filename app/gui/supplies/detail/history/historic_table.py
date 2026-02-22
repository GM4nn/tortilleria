import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from app.gui.components.server_paginated_table import ServerPaginatedTableview
from app.data.providers.supplies import supply_provider
from datetime import datetime

MESES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

MESES_INV = {v: k for k, v in MESES.items()}

COLUMNS = [
    {"text": "Fecha", "stretch": False, "width": 100},
    {"text": "Proveedor", "stretch": False, "width": 120},
    {"text": "Cantidad", "stretch": False, "width": 80},
    {"text": "Unidad", "stretch": False, "width": 70},
    {"text": "Precio Unit.", "stretch": False, "width": 90},
    {"text": "Total", "stretch": False, "width": 90},
    {"text": "Sobro", "stretch": False, "width": 70},
    {"text": "Notas", "stretch": True, "width": 120}
]


class HistoricTable(ttk.Frame):
    """Tabla de historial de compras con paginacion server-side"""

    def __init__(self, parent, supply_id, on_row_click=None):
        super().__init__(parent)
        self.supply_id = supply_id
        self.on_row_click = on_row_click
        self.provider = supply_provider
        self._current_page_data = []

        self.setup_ui()

    def setup_ui(self):
        count = self.provider.count_purchases(self.supply_id)

        if count == 0:
            ttk.Label(
                self,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)
            return

        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=YES)

        self.table = ServerPaginatedTableview(
            master=table_frame,
            coldata=COLUMNS,
            fetch_page=self._fetch_page,
            count_rows=self._count_rows,
            pagesize=10,
            searchable=False,
            bootstyle=PRIMARY,
            height=10
        )
        self.table.pack(fill=BOTH, expand=YES)
        self.table.view.bind('<ButtonRelease-1>', self._on_click)

    def _fetch_page(self, offset, limit):
        purchases = self.provider.get_purchases_paginated(self.supply_id, offset, limit)
        self._current_page_data = purchases

        rows = []
        for purchase in purchases:
            if hasattr(purchase['purchase_date'], 'strftime'):
                fecha = purchase['purchase_date']
                date_str = f"{fecha.day}/{MESES[fecha.month]}/{fecha.year}"
            else:
                date_str = str(purchase['purchase_date'])

            remaining = purchase.get('remaining', 0.0)
            rows.append([
                date_str,
                purchase.get('supplier_name', 'N/A'),
                f"{purchase['quantity']:.2f}",
                purchase['unit'],
                f"${purchase['unit_price']:.2f}",
                f"${purchase['total_price']:.2f}",
                f"{remaining:.2f}" if remaining > 0 else "-",
                purchase['notes'] or ""
            ])

        return rows

    def _count_rows(self):
        return self.provider.count_purchases(self.supply_id)

    def _on_click(self, event):
        if not self.on_row_click:
            return

        item = self.table.view.identify_row(event.y)
        if not item:
            return

        self.table.view.selection_set(item)
        self._process_selection()

    def _process_selection(self):
        selected_items = self.table.view.selection()
        if not selected_items:
            return

        try:
            row_values = self.table.view.item(selected_items[0])['values']
            if not row_values:
                return

            # Buscar en los datos de la pagina actual por indice
            idx = self.table.view.index(selected_items[0])
            if idx < len(self._current_page_data):
                purchase = self._current_page_data[idx]
                self.on_row_click(
                    self.supply_id,
                    None,
                    purchase
                )
                return

            # Fallback: buscar por fecha
            date_str = row_values[0]
            partes = date_str.split('/')
            if len(partes) == 3:
                dia = int(partes[0])
                mes = MESES_INV.get(partes[1], 1)
                anio = int(partes[2])
                purchase_date = datetime(anio, mes, dia).date()
            else:
                purchase_date = datetime.strptime(date_str, "%d/%m/%Y").date()

            for purchase in self._current_page_data:
                p_date = purchase['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
                elif hasattr(p_date, 'date'):
                    p_date = p_date.date()

                if p_date == purchase_date:
                    self.on_row_click(
                        self.supply_id,
                        None,
                        purchase
                    )
                    break

        except Exception as e:
            print(f"Error selecting purchase: {e}")

    def refresh(self):
        if hasattr(self, 'table'):
            self.table.refresh()
