from sqlalchemy.orm import Session
from app.data.database import SessionLocal, engine, init_db
from app.models import Product, Customer, Sale, SaleDetail
from datetime import datetime


class DatabaseManager:
    """
    DatabaseManager using SQLAlchemy ORM.
    This replaces the old sqlite3-based DatabaseManager.
    """

    def __init__(self, db_name="tortilleria.db"):
        """Initialize database and create tables if they don't exist"""

        self._add_default_products()

    def _get_session(self) -> Session:
        """Get a new database session"""
        
        return SessionLocal()

    def _add_default_products(self):
        """Add default products if database is empty"""
        
        db = self._get_session()
        try:
            count = db.query(Product).count()
            if count == 0:
                productos_default = [
                    Product(name="Tortilla de Maíz", price=18.00),
                    Product(name="Tostadas", price=15.00),
                    Product(name="Tlayudas", price=25.00),
                    Product(name="Sopes", price=12.00),
                    Product(name="Tamales", price=20.00),
                    Product(name="Salsa Roja", price=30.00),
                    Product(name="Salsa Verde", price=30.00),
                    Product(name="Frijoles Refritos", price=25.00),
                    Product(name="Quesadillas", price=35.00),
                    Product(name="Gorditas", price=22.00),
                ]
                db.add_all(productos_default)
                db.commit()
        finally:
            db.close()

    # ==================== PRODUCTS METHODS ====================

    def get_products(self):
        """Get all active products"""
        db = self._get_session()
        try:
            products = db.query(Product).filter(Product.active == True).all()
            return [(p.id, p.name, p.price) for p in products]
        finally:
            db.close()

    def add_product(self, name, price):
        """Add a new product"""
        db = self._get_session()
        try:
            product = Product(name=name, price=price)
            db.add(product)
            db.commit()
            db.refresh(product)

            return True, product.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def update_product(self, product_id, name, price):
        """Update an existing product"""
        db = self._get_session()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                product.name = name
                product.price = price
                db.commit()
                return True, "Producto actualizado"
            return False, "Producto no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete_product(self, product_id):
        """Soft delete a product (set active to False)"""
        db = self._get_session()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                product.active = False
                db.commit()
                return True, "Producto eliminado"
            return False, "Producto no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    # ==================== SALES METHODS ====================

    def save_sale(self, items, total):
        """Save a new sale with its details"""
        db = self._get_session()
        try:
            # Create sale
            sale = Sale(total=total)
            db.add(sale)
            db.flush()  # Get the sale.id without committing

            # Create sale details
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

    def get_sales_today(self):
        """Get count and sum of today's sales"""
        db = self._get_session()
        try:
            from sqlalchemy import func, cast, Date

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

    # ==================== CUSTOMERS METHODS ====================

    def get_customers(self):
        """Get all active customers"""
        db = self._get_session()
        try:
            customers = db.query(Customer).filter(Customer.active == True).order_by(Customer.customer_name).all()
            # Return in the same format as the old implementation
            return [
                (c.id, c.customer_name, c.customer_direction, c.customer_category,
                 c.customer_photo, c.customer_phone, c.created_at, c.updated_at)
                for c in customers
            ]
        finally:
            db.close()

    def add_customer(self, name, direction, category, photo, phone):
        """Add a new customer"""
        db = self._get_session()
        try:
            customer = Customer(
                customer_name=name,
                customer_direction=direction,
                customer_category=category,
                customer_photo=photo,
                customer_phone=phone
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            return True, customer.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def update_customer(self, customer_id, name, direction, category, photo, phone):
        """Update an existing customer"""
        db = self._get_session()
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                customer.customer_name = name
                customer.customer_direction = direction
                customer.customer_category = category
                customer.customer_photo = photo
                customer.customer_phone = phone
                customer.updated_at = datetime.now()
                db.commit()
                return True, "Cliente actualizado"
            return False, "Cliente no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete_customer(self, customer_id):
        """Soft delete a customer (set active to False)"""
        db = self._get_session()
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                customer.active = False
                db.commit()
                return True, "Cliente eliminado"
            return False, "Cliente no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()
