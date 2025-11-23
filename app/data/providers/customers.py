from app.data.database import get_db
from app.models import Customer
from datetime import datetime


class CustomerProvider:

    def get_all(self):

        db = get_db()
        
        try:
            customers = db.query(
                Customer.id,
                Customer.customer_name,
                Customer.customer_direction,
                Customer.customer_category,
                Customer.customer_photo,
                Customer.customer_phone,
                Customer.created_at,
                Customer.updated_at
            ).filter(Customer.active == True).order_by(Customer.customer_name).all()
            
            return customers

        finally:
            
            db.close()

    def get_by_id(self, customer_id):
        
        db = get_db()
        
        try:
            customer = db.query(
                Customer.id,
                Customer.customer_name,
                Customer.customer_direction,
                Customer.customer_category,
                Customer.customer_photo,
                Customer.customer_phone,
                Customer.created_at,
                Customer.updated_at
            ).filter(Customer.id == customer_id, Customer.active == True).first()
            
            return customer
        
        finally:
            db.close()

    def add(self, name, direction, category, photo, phone):
        db = get_db()
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

    def update(self, customer_id, name, direction, category, photo, phone):
        db = get_db()
        
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


    def delete(self, customer_id):

        db = get_db()

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

customer_provider = CustomerProvider()