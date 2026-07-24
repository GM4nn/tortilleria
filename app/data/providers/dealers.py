from sqlalchemy.exc import IntegrityError
from app.data.database import get_db
from app.models import Dealer
from app.services.firestore_service import firestore_service


class DealerProvider:

    def get_all(self):
        db = get_db()

        try:
            dealers = db.query(Dealer).filter(
                Dealer.active == True
            ).order_by(Dealer.name).all()
            return [(d.id, d.username, d.pin, d.name) for d in dealers]

        finally:
            db.close()

    def get_all_active_dicts(self):

        db = get_db()
        
        try:
            dealers = db.query(Dealer).filter(
                Dealer.active == True
            ).order_by(Dealer.name).all()
            return [
                {
                    "username": d.username,
                    "display_name": d.name
                } for d in dealers
            ]
        finally:
            db.close()

    def add(self, username, pin, name):
        db = get_db()

        try:
            dealer = Dealer(
                username=username,
                pin=pin,
                name=name
            )

            db.add(dealer)
            db.commit()
            db.refresh(dealer)

            firestore_service.upsert_dealer(
                username,
                pin,
                name
            )
    
            return True, dealer.id
        except IntegrityError:
            db.rollback()
            return False, "Ya existe un repartidor con ese usuario"

        except Exception as e:
            db.rollback()
            return False, str(e)

        finally:
            db.close()

    def update(self, dealer_id, username, pin, name):
        db = get_db()
        try:
            dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

            if not dealer:
                return False, "Repartidor no encontrado"

            old_username = dealer.username
            dealer.username = username
            dealer.pin = pin
            dealer.name = name

            db.commit()

            if old_username != username:
                firestore_service.delete_dealer(old_username)
                
            firestore_service.upsert_dealer(username, pin, name)
            return True, "Repartidor actualizado"
        except IntegrityError:
            db.rollback()
            return False, "Ya existe un repartidor con ese usuario"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete(self, dealer_id):

        db = get_db()
        try:
            dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
           
            if not dealer:
                return False, "Repartidor no encontrado"

            username = dealer.username
            dealer.active = False
            db.commit()
            
            firestore_service.delete_dealer(username)
            return True, "Repartidor eliminado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()


dealer_provider = DealerProvider()
