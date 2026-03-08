from app.models import Order, OrderDetail
from app.models.order_refund import OrderRefund
from sqlalchemy import func, cast, Date, case, literal
from app.data.database import get_db
from app.constants import (
    mexico_now,
    PAYMENT_STATUS_UNPAID,
    PAYMENT_STATUS_PARTIAL,
    PAYMENT_STATUS_PAID,
    ORDER_STATUSES_PENDING,
)


class OrderProvider:

    def save(self, items, total, customer_id, notes=None, amount_paid=0.0):

        db = get_db()
        try:
            order = Order(
                total=total,
                customer_id=customer_id,
                status='pendiente',
                notes=notes,
                amount_paid=amount_paid
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

    def get_all(self, offset=0, limit=None, filters=None):

        db = get_db()

        try:
            query = db.query(
                Order.id,
                Order.date,
                Order.total,
                Order.status,
                Order.customer_id,
                Order.amount_paid
            )

            if filters:
                query = query.filter(*filters)

            query = query.order_by(Order.date.desc())

            if limit is not None:
                print(limit)
                print(offset)
                query = query.offset(offset).limit(limit)

            return query.all()

        finally:
            db.close()

    def get_count(self, filters=None):

        db = get_db()

        try:
            query = db.query(func.count(Order.id))
            if filters:
                query = query.filter(*filters)
            return query.scalar() or 0
        finally:
            db.close()

    def build_status_filter(self, status):
        return [Order.status == status]

    def build_customer_filter(self, customer_id):
        return [Order.customer_id == customer_id]

    def build_payment_status_filter(self, payment_status):
        paid = func.coalesce(Order.amount_paid, 0.0)
        if payment_status == PAYMENT_STATUS_UNPAID:
            return [paid <= 0]
        elif payment_status == PAYMENT_STATUS_PARTIAL:
            return [paid > 0, paid < Order.total]
        elif payment_status == PAYMENT_STATUS_PAID:
            return [paid >= Order.total]
        return []

    def build_date_range_filter(self, start_date, end_date):
        return [
            func.date(Order.date) >= start_date.isoformat(),
            func.date(Order.date) <= end_date.isoformat()
        ]

    def get_pending(self):

        db = get_db()

        try:
            orders = db.query(
                Order.id,
                Order.date,
                Order.total,
                Order.status,
                Order.customer_id,
                Order.amount_paid
            ).filter(
                Order.status == ORDER_STATUSES_PENDING
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
                    'amount_paid': order.amount_paid or 0.0,
                    'payment_status': order.payment_status,
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
                Order.status,
                Order.amount_paid
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

    def register_payment(self, order_id, amount):
        db = get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False, "Pedido no encontrado"

            current_paid = order.amount_paid or 0.0
            new_paid = current_paid + amount

            if new_paid > order.total:
                return False, f"El monto excede el total del pedido (${order.total:.2f})"

            order.amount_paid = new_paid
            db.commit()
            return True, order_id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def complete_order(self, order_id, refund_items, final_payment=0.0):
        db = get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False, "Pedido no encontrado"

            # Aplicar pago final si hay
            if final_payment > 0:
                order.amount_paid = (order.amount_paid or 0.0) + final_payment

            # Validar que esté completamente pagado
            if round(order.amount_paid or 0.0, 2) != round(order.total, 2):
                return False, f"El pedido no está completamente pagado. Pagado: ${order.amount_paid or 0.0:.2f}, Total: ${order.total:.2f}"

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
