from app.models import Order, OrderDetail
from sqlalchemy import func, cast, Date
from app.data.database import get_db
from datetime import datetime


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

    def get_today(self):

        db = get_db()

        try:
            today = datetime.now().date()

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
