import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from app.data.providers.cash_cut import cash_cut_provider
from app.constants import mexico_now


class RegisterForm(ttk.Labelframe):
    def __init__(self, parent, content):
        super().__init__(parent, text="Registrar Corte", padding=15)
        self.content = content
        self.provider = cash_cut_provider
        self.setup_ui()

    def setup_ui(self):
        # Payment method entries
        fields = [
            ("Efectivo:", "cash"),
            ("Tarjeta:", "card"),
            ("Transferencia:", "transfer"),
        ]

        self.entries = {}
        for label_text, key in fields:
            row = ttk.Frame(self)
            row.pack(fill=X, pady=3)

            ttk.Label(
                row,
                text=label_text,
                font=("Segoe UI", 11),
                width=14,
                anchor=W,
            ).pack(side=LEFT)

            entry = ttk.Entry(row, font=("Segoe UI", 11), width=15)
            entry.insert(0, "0.00")
            entry.pack(side=LEFT, fill=X, expand=YES)
            entry.bind("<KeyRelease>", self._update_totals)
            entry.bind("<FocusIn>", lambda e, en=entry: self._select_all(en))
            self.entries[key] = entry

        # Separator
        ttk.Separator(self).pack(fill=X, pady=10)

        # Total declared
        total_row = ttk.Frame(self)
        total_row.pack(fill=X, pady=2)

        ttk.Label(
            total_row,
            text="Total Declarado:",
            font=("Segoe UI", 11, "bold"),
            width=14,
            anchor=W,
        ).pack(side=LEFT)

        self.lbl_declared = ttk.Label(
            total_row,
            text="$0.00",
            font=("Segoe UI", 14, "bold"),
            bootstyle="primary",
        )
        self.lbl_declared.pack(side=LEFT)

        # Difference
        diff_row = ttk.Frame(self)
        diff_row.pack(fill=X, pady=2)

        ttk.Label(
            diff_row,
            text="Diferencia:",
            font=("Segoe UI", 11, "bold"),
            width=14,
            anchor=W,
        ).pack(side=LEFT)

        self.lbl_difference = ttk.Label(
            diff_row,
            text="$0.00",
            font=("Segoe UI", 14, "bold"),
        )
        self.lbl_difference.pack(side=LEFT)

        # Notes
        ttk.Label(
            self,
            text="Notas (opcional):",
            font=("Segoe UI", 10),
        ).pack(anchor=W, pady=(10, 3))

        self.txt_notes = ttk.Text(self, height=2, font=("Segoe UI", 10))
        self.txt_notes.pack(fill=X)

        # Register button
        self.btn_register = ttk.Button(
            self,
            text="Registrar Corte de Caja",
            command=self._register_cut,
            bootstyle="success",
        )
        self.btn_register.pack(fill=X, pady=(15, 0), ipady=10)

    def _select_all(self, entry):
        entry.select_range(0, "end")

    def _parse_entry(self, key):
        try:
            val = float(self.entries[key].get().replace(",", "").strip())
            return max(val, 0.0)
        except (ValueError, AttributeError):
            return 0.0

    def _update_totals(self, event=None):
        cash = self._parse_entry("cash")
        card = self._parse_entry("card")
        transfer = self._parse_entry("transfer")
        declared = cash + card + transfer

        self.lbl_declared.config(text=f"${declared:,.2f}")

        expected = getattr(self.content, 'current_summary', {}).get('expected_total', 0.0)
        diff = declared - expected

        if abs(diff) < 0.01:
            self.lbl_difference.config(text="$0.00  Exacto", bootstyle="success")
        elif diff > 0:
            self.lbl_difference.config(text=f"+${diff:,.2f}  Sobrante", bootstyle="info")
        else:
            self.lbl_difference.config(text=f"-${abs(diff):,.2f}  Faltante", bootstyle="danger")

    def _register_cut(self):
        summary = getattr(self.content, 'current_summary', None)
        if not summary:
            Messagebox.show_error("No se pudo obtener el resumen del dia.", "Error")
            return

        # Check if already cut today
        existing = self.provider.get_today_cut()
        if existing:
            Messagebox.show_warning(
                f"Ya se registro un corte de caja hoy (#{existing['id']}).\nSolo se permite un corte por dia.",
                "Corte Ya Registrado",
            )
            return

        if summary['sales_count'] == 0 and summary['orders_count'] == 0:
            Messagebox.show_warning(
                "No hay ventas ni pedidos hoy.\nNo es necesario hacer un corte.",
                "Sin Movimientos",
            )
            return

        cash = self._parse_entry("cash")
        card = self._parse_entry("card")
        transfer = self._parse_entry("transfer")
        declared = cash + card + transfer
        difference = declared - summary['expected_total']

        notes = self.txt_notes.get("1.0", "end").strip()

        today_str = summary['today'].strftime("%d/%b/%Y")

        # Confirmation
        msg = (
            f"Corte del dia: {today_str}\n"
            f"Ventas: {summary['sales_count']}  |  Pedidos: {summary['orders_count']}\n"
            f"Total Esperado: ${summary['expected_total']:,.2f}\n"
            f"Total Declarado: ${declared:,.2f}\n"
            f"Diferencia: ${difference:,.2f}\n\n"
        )

        result = Messagebox.yesno(
            f"{msg}Confirmar el corte de caja?",
            "Confirmar Corte",
        )

        if result != "Yes":
            return

        opened_at = mexico_now().replace(hour=0, minute=0, second=0, microsecond=0)

        data = {
            'opened_at': opened_at,
            'sales_count': summary['sales_count'],
            'orders_count': summary['orders_count'],
            'sales_total': summary['sales_total'],
            'orders_total': summary['orders_total'],
            'expected_total': summary['expected_total'],
            'declared_cash': cash,
            'declared_card': card,
            'declared_transfer': transfer,
            'declared_total': declared,
            'difference': difference,
            'notes': notes if notes else None,
        }

        success, result_id = self.provider.save(data)

        if success:
            Messagebox.show_info(
                f"Corte de caja #{result_id} registrado correctamente.",
                "Corte Registrado",
            )
            self.content.refresh_all()
        else:
            Messagebox.show_error(f"Error al registrar el corte:\n{result_id}", "Error")

    def reset_form(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
            entry.insert(0, "0.00")
        self.txt_notes.delete("1.0", "end")
        self._update_totals()
