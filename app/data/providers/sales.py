from sqlalchemy import func, cast, Date
from app.models import Sale, SaleDetail
from app.data.database import get_db
from datetime import datetime


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
            today = datetime.now().date()

            result = db.query(
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total), 0.0)
            ).filter(
                cast(Sale.date, Date) == today
            ).first()

            return result[0] or 0, result[1] or 0.0
        
        finally:
            db.close()


    def get_all(self):

        db = get_db()

        try:

            sales = db.query(Sale.id,
                Sale.date,
                Sale.total,
                Sale.customer_id
            ).order_by(Sale.date.desc()).all()
            return sales

        finally:
            db.close()


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


    def get_by_date_range(self, start_date, end_date):

        db = get_db()

        try:
            sales = db.query(Sale.id,
                Sale.date,
                Sale.total,
                Sale.customer_id
            ).filter(
                cast(Sale.date, Date) >= start_date,
                cast(Sale.date, Date) <= end_date
            ).order_by(Sale.date.desc()).all()

            return sales

        finally:
            db.close()


sale_provider = SaleProvider()
