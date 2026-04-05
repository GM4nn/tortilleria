from firebase_admin import credentials, firestore
import firebase_admin
import os
from app.constants import (
    ORDERS_COLLECTION,
    ORDER_STATUSES_PENDING,
    SERVICE_ACCOUNT_PATH,
)


class FirestoreService:

    def __init__(self):
        self._db = None
        self.available = False
        self._initialize()

    def _initialize(self):

        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            return

        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)

            self._db = firestore.client()
            self.available = True

        except Exception as e:
            print(f"[Firestore] Error in initialization: {e}")

    def add_order(
        self,
        order_id,
        customer_name,
        items,
        total,
        amount_paid,
        created_at
    ):

        if not self.available:
            return

        try:
            doc_ref = self._db.collection(ORDERS_COLLECTION).document(str(order_id))
            doc_ref.set(
                {
                    "order_id": order_id,
                    "customer_name": customer_name,
                    "items": [
                        {
                            "product_id": item["id"],
                            "name": item["name"],
                            "price": item["price"],
                            "quantity": item["quantity"],
                            "subtotal": item["subtotal"],
                        }
                        for item in items
                    ],
                    "total": total,
                    "amount_paid": amount_paid,
                    "status": ORDER_STATUSES_PENDING,
                    "created_at": created_at,
                }
            )
            return doc_ref.id

        except Exception as e:
            print(f"[Firestore] Error in sync order #{order_id}: {e}")

    def update_order_status(
        self,
        order_id,
        status
    ):

        if not self.available:
            return

        try:
            self._db.collection(ORDERS_COLLECTION).\
                document(str(order_id)).\
                update(
                    {
                        "status": status
                    }
                )
        except Exception as e:
            print(f"[Firestore] Error in update order #{order_id}: {e}")


    def sync_payment(self, order_id, amount_paid):
        if not self.available:
            return

        try:
            self._db.collection(ORDERS_COLLECTION).\
                document(str(order_id)).\
                update(
                    {"amount_paid": amount_paid}
                )
        except Exception as e:
            print(f"[Firestore] Error in sync payment #{order_id}: {e}")


firestore_service = FirestoreService()
