import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from datetime import datetime


class historyTab(ttk.Frame):
    """Tab de history de compras: tabla paginada con selección para editar"""

    def __init__(self, parent, supply_data, on_edit_purchase_callback=None):
        super().__init__(parent)
        self.supply_data = supply_data
        self.on_edit_purchase_callback = on_edit_purchase_callback

        self.setup_ui()

    def setup_ui(self):
        if self.supply_data['purchases']:
            columns = [
                {"text": "Fecha", "stretch": False, "width": 100},
                {"text": "Proveedor", "stretch": False, "width": 120},
                {"text": "Cantidad", "stretch": False, "width": 80},
                {"text": "Unidad", "stretch": False, "width": 80},
                {"text": "Precio Unit.", "stretch": False, "width": 100},
                {"text": "Total", "stretch": False, "width": 100},
                {"text": "Notas", "stretch": True, "width": 150}
            ]

            table_frame = ttk.Frame(self)
            table_frame.pack(fill=BOTH, expand=YES)

            self.purchases_table = Tableview(
                master=table_frame,
                coldata=columns,
                rowdata=[],
                paginated=True,
                searchable=False,
                bootstyle=PRIMARY,
                pagesize=10,
                height=10
            )
            self.purchases_table.pack(fill=BOTH, expand=YES)

            self.purchases_table.view.bind('<ButtonRelease-1>', self._on_purchase_clicked)

            self._fill_table()
        else:
            ttk.Label(
                self,
                text="No hay compras registradas para este insumo",
                font=("Arial", 10),
                bootstyle="secondary"
            ).pack(pady=20)

    def _fill_table(self):
        self.purchases_table.delete_rows()

        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        rows = []
        for purchase in self.supply_data['purchases']:
            if hasattr(purchase['purchase_date'], 'strftime'):
                fecha = purchase['purchase_date']
                date_str = f"{fecha.day}/{meses[fecha.month]}/{fecha.year}"
            else:
                date_str = str(purchase['purchase_date'])

            rows.append([
                date_str,
                purchase.get('supplier_name', 'N/A'),
                f"{purchase['quantity']:.2f}",
                purchase['unit'],
                f"${purchase['unit_price']:.2f}",
                f"${purchase['total_price']:.2f}",
                purchase['notes'] or ""
            ])

        if rows:
            self.purchases_table.insert_rows(0, rows)

        self.purchases_table.load_table_data()

    def _on_purchase_clicked(self, event):
        if not self.on_edit_purchase_callback:
            return

        item = self.purchases_table.view.identify_row(event.y)
        if not item:
            return

        self.purchases_table.view.selection_set(item)
        self._process_selection()

    def _process_selection(self):
        if not self.on_edit_purchase_callback:
            return

        selected_items = self.purchases_table.view.selection()
        if not selected_items:
            return

        try:
            selected_iid = selected_items[0]
            row_values = self.purchases_table.view.item(selected_iid)['values']
            if not row_values:
                return

            date_str = row_values[0]

            meses_inv = {
                'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
            }

            partes = date_str.split('/')
            if len(partes) == 3:
                dia = int(partes[0])
                mes = meses_inv.get(partes[1], 1)
                anio = int(partes[2])
                purchase_date = datetime(anio, mes, dia).date()
            else:
                purchase_date = datetime.strptime(date_str, "%d/%m/%Y").date()

            selected_purchase = None
            for purchase in self.supply_data['purchases']:
                p_date = purchase['purchase_date']
                if isinstance(p_date, str):
                    p_date = datetime.strptime(p_date, "%Y-%m-%d").date()
                elif hasattr(p_date, 'date'):
                    p_date = p_date.date()

                if p_date == purchase_date:
                    selected_purchase = purchase
                    break

            if selected_purchase and self.on_edit_purchase_callback:
                self.on_edit_purchase_callback(
                    self.supply_data['id'],
                    self.supply_data['supply_name'],
                    selected_purchase
                )

        except Exception as e:
            print(f"Error selecting purchase for edit: {e}")

    def refresh(self, supply_data):
        """Refresh table with new data"""
        self.supply_data = supply_data
        if hasattr(self, 'purchases_table'):
            self._fill_table()
