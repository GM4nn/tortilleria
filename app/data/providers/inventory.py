import csv

from app.data.database import get_db
from app.constants import CSV_PATH
from app.models import Product


class InventoryProvider:

    def _add_default_products(self):

        db = get_db()

        try:
            count = db.query(Product).count()

            if count == 0:
                with open(CSV_PATH, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    productos = [
                        Product(
                            icon=row['icon'],
                            name=row['name'],
                            price=float(row['price'])
                        )
                        for row in reader
                    ]

                db.add_all(productos)
                db.commit()

        finally:
            db.close()

    def get_all(self):

        db = get_db()

        try:
            products = db.query(
                Product.id,
                Product.icon,
                Product.name,
                Product.price
            ).filter(Product.active == True).all()

            return products
        finally:
            db.close()

    def get_by_id(self, product_id):

        db = get_db()
        
        try:
            
            product = db.query(
                Product.id,
                Product.name,
                Product.price
            ).filter(Product.id == product_id, Product.active == True).first()
            
            return product
        finally:
            db.close()

    def add(self, icon, name, price):

        db = get_db()

        try:
            product = Product(icon=icon, name=name, price=price)
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            return True, product.id
       
        except Exception as e:
            
            db.rollback()
            return False, str(e)
        
        finally:
            db.close()


    def update(self, product_id, icon, name, price):

        db = get_db()

        try:
            product = db.query(Product).filter(Product.id == product_id).first()

            if product:
                product.icon = icon
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

            
    def delete(self, product_id):

        db = get_db()
        
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


inventory_provider = InventoryProvider()