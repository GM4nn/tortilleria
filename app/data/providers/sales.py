from sqlalchemy import func, cast, Date
from app.models import Sale, SaleDetail
from app.data.database import get_db
from app.constants import mexico_now


class SaleProvider:


    def save(self, items, total, customer_id):

        db = get_db()
        try:
            sale = Sale(total=total, customer_id=customer_id)
            db.add(sale)
            db.flush()

            for item in items:
                detail = SaleDetail(
                    sale_id=sale.id,
                    product_id=item['id'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                    subtotal=item['subtotal']
                )
                db.add(detail)

            db.commit()
            return True, sale.id
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
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total), 0.0)
            ).filter(
                cast(Sale.date, Date) == today
            ).first()

            return result[0] or 0, result[1] or 0.0
        
        finally:
            db.close()


    def get_all(self, offset=0, limit=None, filters=None):

        db = get_db()

        try:
            query = db.query(
                Sale.id,
                Sale.date,
                Sale.total,
                Sale.customer_id
            )

            if filters:
                query = query.filter(*filters)

            query = query.order_by(Sale.date.desc())

            if limit is not None:
                query = query.offset(offset).limit(limit)

            return query.all()

        finally:
            db.close()

    def get_count(self, filters=None):

        db = get_db()

        try:
            query = db.query(func.count(Sale.id))
            if filters:
                query = query.filter(*filters)
            return query.scalar() or 0
        finally:
            db.close()

    def build_date_range_filter(self, start_date, end_date):
        return [
            func.date(Sale.date) >= start_date.isoformat(),
            func.date(Sale.date) <= end_date.isoformat()
        ]


    def get_by_id(self, sale_id):

        db = get_db()

        try:
            sale = db.query(Sale).filter(Sale.id == sale_id).first()

            if sale:
                return {
                    'id': sale.id,
                    'date': sale.date,
                    'total': sale.total,
                    'customer_id': sale.customer_id,
                    'details': [
                        {
                            'product_id': d.product_id,
                            'product_name': d.product.name if d.product else 'N/A',
                            'quantity': d.quantity,
                            'unit_price': d.unit_price,
                            'subtotal': d.subtotal
                        }
                        for d in sale.sales_details
                    ]
                }
            return None
        finally:
            db.close()



sale_provider = SaleProvider()
