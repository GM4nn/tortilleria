from app.models.order_refund import OrderRefund
from app.data.database import get_db


class RefundProvider:

    def get_by_order(self, order_id):
        db = get_db()
        try:
            refunds = db.query(OrderRefund).filter(
                OrderRefund.order_id == order_id
            ).all()

            return [
                {
                    'id': r.id,
                    'product_id': r.product_id,
                    'product_name': r.product.name if r.product else 'N/A',
                    'quantity': r.quantity,
                    'comments': r.comments
                }
                for r in refunds
            ]
        finally:
            db.close()


refund_provider = RefundProvider()
