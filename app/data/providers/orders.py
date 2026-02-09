from app.models import Order, OrderDetail
from app.models.order_refund import OrderRefund
from sqlalchemy import func, cast, Date
from app.data.database import get_db
from app.constants import mexico_now


class OrderProvider:

    def save(self, items, total, customer_id, notes=None):

        db = get_db()
        try:
            order = Order(
                total=total,
                customer_id=customer_id,
                status='pendiente',
                notes=notes
            )
            db.add(order)
            db.flush()

            for item in items:
                detail = OrderDetail(
                    order_id=order.id,
                    product_id=item['id'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    subtotal=item['subtotal']
                )
                db.add(detail)

            db.commit()
            return True, order.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def get_all(self):

        db = get_db()

        try:
            orders = db.query(
                Order.id,
                Order.date,
                Order.total,
                Order.status,
                Order.customer_id
            ).order_by(Order.date.desc()).all()
            return orders

        finally:
            db.close()

    def get_pending(self):

        db = get_db()

        try:
            orders = db.query(
                Order.id,
                Order.date,
                Order.total,
                Order.status,
                Order.customer_id
            ).filter(
                Order.status == 'pendiente'
            ).order_by(Order.date.desc()).all()
            return orders

        finally:
            db.close()

    def get_by_id(self, order_id):

        db = get_db()

        try:
            order = db.query(Order).filter(Order.id == order_id).first()

            if order:
                return {
                    'id': order.id,
                    'date': order.date,
                    'total': order.total,
                    'status': order.status,
                    'completed_at': order.completed_at,
                    'customer_id': order.customer_id,
                    'notes': order.notes,
                    'details': [
                        {
                            'product_id': d.product_id,
                            'product_name': d.product.name if d.product else 'N/A',
                            'quantity': d.quantity,
                            'unit_price': d.unit_price,
                            'subtotal': d.subtotal
                        }
                        for d in order.order_details
                    ]
                }
            return None
        finally:
            db.close()

    def get_by_customer(self, customer_id):

        db = get_db()

        try:
            orders = db.query(
                Order.id,
                Order.date,
                Order.total,
                Order.status
            ).filter(
                Order.customer_id == customer_id
            ).order_by(Order.date.desc()).all()
            return orders

        finally:
            db.close()

    def update_status(self, order_id, new_status):

        db = get_db()

        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.status = new_status
                db.commit()
                return True, order_id
            return False, "Pedido no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def complete_order(self, order_id, refund_items):
        db = get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False, "Pedido no encontrado"

            # Guardar reembolsos
            for item in refund_items:
                refund = OrderRefund(
                    order_id=order_id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    comments=item.get('comments')
                )
                db.add(refund)

            # Marcar como completado
            order.status = 'completado'
            order.completed_at = mexico_now()
            db.commit()
            return True, order_id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def get_today(self):

        db = get_db()

        try:
            today = mexico_now().date()

            result = db.query(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total), 0.0)
            ).filter(
                cast(Order.date, Date) == today
            ).first()

            return result[0] or 0, result[1] or 0.0

        finally:
            db.close()


order_provider = OrderProvider()
