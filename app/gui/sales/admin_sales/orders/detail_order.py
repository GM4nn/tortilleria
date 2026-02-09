import ttkbootstrap as ttk
import tkinter.messagebox as mb
from ttkbootstrap.constants import *
from app.data.providers.orders import order_provider
from app.data.providers.refunds import refund_provider
from app.gui.sales.admin_sales.orders.refund_dialog import RefundDialog
from app.constants import ORDER_STATUSES, ORDER_STATUSES_COMPLETE, ORDER_STATUSES_PENDING


class DetailOrder(ttk.Labelframe):
    def __init__(self, parent, customers_cache, on_order_changed):
        super().__init__(parent, text="  Detalles del Pedido  ", padding=10, width=350)
        self.customers_cache = customers_cache
        self.on_order_changed = on_order_changed

        self.setup_ui()

    def setup_ui(self):
        self.pack_propagate(False)

        self.detail_content = ttk.Frame(self)
        self.detail_content.pack(fill=BOTH, expand=YES)

        self.no_selection_label = ttk.Label(
            self.detail_content,
            text="Selecciona un pedido\npara ver sus detalles",
            font=("Arial", 12),
            bootstyle="secondary",
            justify=CENTER
        )
        self.no_selection_label.pack(expand=YES)

    def show_order_details(self, order):
        for widget in self.detail_content.winfo_children():
            widget.destroy()

        order_data = order_provider.get_by_id(order.id)

        if not order_data:
            ttk.Label(
                self.detail_content,
                text="Error al cargar detalles",
                bootstyle="danger"
            ).pack(pady=20)
            return

        self._render_header(order_data)
        ttk.Separator(self.detail_content).pack(fill=X, pady=10)

        self._render_customer_and_status(order_data)
        ttk.Separator(self.detail_content).pack(fill=X, pady=10)

        self._render_products(order_data['details'])
        self._render_total(order_data['total'])

        if order_data['status'] == ORDER_STATUSES_COMPLETE:
            self._show_refunds_section(order_data['id'])

        if order_data['status'] == ORDER_STATUSES_PENDING:
            self._render_actions(order_data)

    def _render_header(self, order_data):
        ttk.Label(
            self.detail_content,
            text=f"Pedido #{order_data['id']}",
            font=("Arial", 16, "bold")
        ).pack(anchor=W)

        date_str = order_data['date'].strftime("%d/%m/%Y %H:%M") if order_data['date'] else "N/A"
        ttk.Label(
            self.detail_content,
            text=f"Fecha de pedido: {date_str}",
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(anchor=W)

        if order_data.get('completed_at'):
            completed_str = order_data['completed_at'].strftime("%d/%m/%Y %H:%M")
            ttk.Label(
                self.detail_content,
                text=f"Fecha de completado: {completed_str}",
                font=("Arial", 10),
                bootstyle="success"
            ).pack(anchor=W)

    def _render_customer_and_status(self, order_data):
        customer_name = self.customers_cache.get(order_data['customer_id'], "Cliente desconocido")
        client_frame = ttk.Frame(self.detail_content)
        client_frame.pack(fill=X)

        ttk.Label(client_frame, text="Cliente:", font=("Arial", 10, "bold")).pack(side=LEFT)
        ttk.Label(client_frame, text=customer_name, font=("Arial", 10)).pack(side=LEFT, padx=(5, 0))

        status_frame = ttk.Frame(self.detail_content)
        status_frame.pack(fill=X, pady=(5, 0))

        ttk.Label(status_frame, text="Estado:", font=("Arial", 10, "bold")).pack(side=LEFT)

        status_info = ORDER_STATUSES.get(order_data['status'], {"label": order_data['status'], "color": "secondary"})

        ttk.Label(
            status_frame,
            text=f"  {status_info['label']}  ",
            font=("Arial", 9, "bold"),
            bootstyle=f"inverse-{status_info['color']}"
        ).pack(side=LEFT, padx=(5, 0))

    def _render_products(self, details):
        ttk.Label(
            self.detail_content,
            text="Productos:",
            font=("Arial", 11, "bold")
        ).pack(anchor=W)

        products_frame = ttk.Frame(self.detail_content)
        products_frame.pack(fill=BOTH, expand=YES, pady=(5, 10))

        for detail in details:
            item_frame = ttk.Frame(products_frame, bootstyle="light")
            item_frame.pack(fill=X, pady=2)

            item_content = ttk.Frame(item_frame)
            item_content.pack(fill=X, padx=8, pady=6)

            ttk.Label(
                item_content,
                text=f"{detail['product_name']}",
                font=("Arial", 10, "bold")
            ).pack(anchor=W)

            detail_row = ttk.Frame(item_content)
            detail_row.pack(fill=X)

            ttk.Label(
                detail_row,
                text=f"x{detail['quantity']:.0f} @ ${detail['unit_price']:.2f}",
                font=("Arial", 9),
                bootstyle="secondary"
            ).pack(side=LEFT)

            ttk.Label(
                detail_row,
                text=f"${detail['subtotal']:.2f}",
                font=("Arial", 10, "bold"),
                bootstyle="success"
            ).pack(side=RIGHT)

    def _render_total(self, total):
        total_frame = ttk.Frame(self.detail_content, bootstyle="dark")
        total_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(
            total_frame,
            text="TOTAL:",
            font=("Arial", 12, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=LEFT, padx=10, pady=8)

        ttk.Label(
            total_frame,
            text=f"${total:.2f}",
            font=("Arial", 16, "bold"),
            bootstyle="inverse-dark"
        ).pack(side=RIGHT, padx=10, pady=8)

    def _render_actions(self, order_data):
        btn_frame = ttk.Frame(self.detail_content)
        btn_frame.pack(fill=X)

        ttk.Button(
            btn_frame,
            text="Marcar Completado",
            command=lambda: self.complete_order(order_data),
            bootstyle="success"
        ).pack(fill=X, pady=2)

        ttk.Button(
            btn_frame,
            text="Cancelar Pedido",
            command=lambda: self.update_order_status(order_data['id'], 'cancelado'),
            bootstyle="danger-outline"
        ).pack(fill=X, pady=2)

    def _show_refunds_section(self, order_id):
        refunds = refund_provider.get_by_order(order_id)

        refunds_with_return = [r for r in refunds if r['quantity'] > 0]

        if not refunds_with_return:
            return

        ttk.Separator(self.detail_content).pack(fill=X, pady=5)

        ttk.Label(
            self.detail_content,
            text="Devoluciones:",
            font=("Arial", 11, "bold"),
            bootstyle="danger"
        ).pack(anchor=W)

        refunds_frame = ttk.Frame(self.detail_content)
        refunds_frame.pack(fill=X, pady=(5, 0))

        for refund in refunds_with_return:
            item_frame = ttk.Frame(refunds_frame, bootstyle="danger", relief="solid", borderwidth=2)
            item_frame.pack(fill=X, pady=3)

            item_content = ttk.Frame(item_frame)
            item_content.pack(fill=X, padx=10, pady=8)

            ttk.Label(
                item_content,
                text=f"Del producto {refund['product_name']} se devolvio {refund['quantity']:.0f}",
                font=("Arial", 10, "bold"),
                bootstyle="danger",
                wraplength=280
            ).pack(anchor=W)

            if refund.get('comments'):
                ttk.Label(
                    item_content,
                    text=f"Comentarios: {refund['comments']}",
                    font=("Arial", 9),
                    bootstyle="danger",
                    wraplength=280
                ).pack(anchor=W, pady=(4, 0))

    def complete_order(self, order_data):
        dialog = RefundDialog(self.winfo_toplevel(), order_data)
        self.wait_window(dialog)

        if dialog.result is None:
            return

        success, result = order_provider.complete_order(order_data['id'], dialog.result)

        if success:
            mb.showinfo("Éxito", f"Pedido #{order_data['id']} completado")
            self.on_order_changed()
            self.reset_panel()
        else:
            mb.showerror("Error", f"Error al completar: {result}")

    def update_order_status(self, order_id, new_status):
        if not mb.askyesno("Confirmar", "¿Desea cancelar este pedido?"):
            return

        success, result = order_provider.update_status(order_id, new_status)

        if success:
            mb.showinfo("Éxito", f"Pedido #{order_id} actualizado")
            self.on_order_changed()
            self.reset_panel()
        else:
            mb.showerror("Error", f"Error al actualizar: {result}")

    def reset_panel(self):
        for widget in self.detail_content.winfo_children():
            widget.destroy()

        self.no_selection_label = ttk.Label(
            self.detail_content,
            text="Selecciona un pedido\npara ver sus detalles",
            font=("Arial", 12),
            bootstyle="secondary",
            justify=CENTER
        )
        self.no_selection_label.pack(expand=YES)
