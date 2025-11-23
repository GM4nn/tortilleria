from app.data.database import get_db
from app.models import Product


class InventoryProvider:

    def _add_default_products(self):

        db = get_db()
        
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

    def get_all(self):

        db = get_db()

        try:
            products = db.query(
                Product.id,
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

    def add(self, name, price):

        db = get_db()
        
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


    def update(self, product_id, name, price):
        
        db = get_db()

        try:
            product = db.query(Product.id,
                Product.name,
                Product.price
            ).filter(Product.id == product_id).first()

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