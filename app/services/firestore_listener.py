from app.services.firestore_service import firestore_service
from app.data.providers.orders import order_provider
from app.gui.components.toast import Toast
from app.constants import ORDERS_COLLECTION, ORDER_STATUSES_COMPLETE


class FirestoreOrderListener:

    def __init__(self):
        self._app = None
        self.on_order_changed = None

    def start(self, app):
        self._app = app

        if not firestore_service.available:
            return

        collection_ref = firestore_service._db.collection(ORDERS_COLLECTION)
        collection_ref.on_snapshot(self._on_snapshot)

    def _on_snapshot(
        self,
        _snapshot,
        changes,
        _read_time
    ):
        modified = next(
            (c for c in changes if c.type.name == "MODIFIED"),
            None
        )

        if not modified:
            return

        data = modified.document.to_dict()
        order_id = data.get("order_id")
        status = data.get("status")

        amount_paid = data.get("amount_paid", 0)
        self._app.root.after(0, self._handle_order_modified, order_id, status, amount_paid)

    def _handle_order_modified(
        self,
        order_id,
        status,
        amount_paid
    ):
        if status == ORDER_STATUSES_COMPLETE:
            order_provider.update_status(order_id, ORDER_STATUSES_COMPLETE)

        order_provider.sync_payment(order_id, amount_paid)
        self._notify_change()

        if status == ORDER_STATUSES_COMPLETE:
            Toast(
                self._app.root,
                f"Pedido #{order_id} completado desde móvil",
                on_action=lambda: self._go_to_order(order_id),
                action_text="Ver pedido",
            )

    def _notify_change(self):
        try:
            if self.on_order_changed:
                self.on_order_changed()
        except Exception:
            self.on_order_changed = None

    def _go_to_order(self, order_id):
        self._app.navigation.change_view("sales_admin", "sales_menu")
        self._app.root.after(100, lambda: self._select_order(order_id))

    def _select_order(self, order_id):
        content = self._app.content

        if hasattr(content, "notebook") and hasattr(content, "tab_pedidos"):
            content.notebook.select(content.tab_pedidos)
            content.orders_list.detail_order.show_order_details(order_id)


firestore_listener = FirestoreOrderListener()
