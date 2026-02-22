from app.data.database import get_db
from app.models import CustomerProductPrice


class CustomerPriceProvider:

    def get_prices_for_customer(self, customer_id):
        """Retorna dict {product_id: custom_price} para un cliente."""
        db = get_db()

        try:
            rows = db.query(
                CustomerProductPrice.product_id,
                CustomerProductPrice.custom_price
            ).filter(
                CustomerProductPrice.customer_id == customer_id
            ).all()

            return {product_id: price for product_id, price in rows}
        finally:
            db.close()

    def save_price(self, customer_id, product_id, price):
        """Guarda o actualiza el precio personalizado de un producto para un cliente."""
        db = get_db()

        try:
            existing = db.query(CustomerProductPrice).filter(
                CustomerProductPrice.customer_id == customer_id,
                CustomerProductPrice.product_id == product_id
            ).first()

            if existing:
                existing.custom_price = price
            else:
                record = CustomerProductPrice(
                    customer_id=customer_id,
                    product_id=product_id,
                    custom_price=price
                )
                db.add(record)

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()


customer_price_provider = CustomerPriceProvider()
