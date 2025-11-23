from sqlalchemy.orm import Session
from app.data.database import SessionLocal
from app.models import Supply, Supplier
from datetime import datetime


class SupplyProvider:
    """Provider para operaciones CRUD de insumos"""

    def _get_session(self) -> Session:
        """Get a new database session"""
        return SessionLocal()

    def get_all(self):
        """Get all supplies with supplier info"""
        db = self._get_session()
        try:
            supplies = db.query(Supply).order_by(Supply.purchase_date.desc()).all()
            return [
                {
                    'id': s.id,
                    'supply_name': s.supply_name,
                    'supplier_id': s.supplier_id,
                    'supplier_name': s.supplier.supplier_name if s.supplier else 'N/A',
                    'quantity': s.quantity,
                    'unit': s.unit,
                    'unit_price': s.unit_price,
                    'total_price': s.total_price,
                    'purchase_date': s.purchase_date,
                    'notes': s.notes,
                    'created_at': s.created_at,
                    'updated_at': s.updated_at
                }
                for s in supplies
            ]
        finally:
            db.close()

    def get_by_id(self, supply_id):
        """Get a supply by ID"""
        db = self._get_session()
        try:
            supply = db.query(Supply).filter(Supply.id == supply_id).first()
            if supply:
                return {
                    'id': supply.id,
                    'supply_name': supply.supply_name,
                    'supplier_id': supply.supplier_id,
                    'supplier_name': supply.supplier.supplier_name if supply.supplier else 'N/A',
                    'quantity': supply.quantity,
                    'unit': supply.unit,
                    'unit_price': supply.unit_price,
                    'total_price': supply.total_price,
                    'purchase_date': supply.purchase_date,
                    'notes': supply.notes
                }
            return None
        finally:
            db.close()

    def add(self, supply_name, supplier_id, quantity, unit, unit_price, total_price, purchase_date, notes):
        """Add a new supply"""
        db = self._get_session()
        try:
            supply = Supply(
                supply_name=supply_name,
                supplier_id=supplier_id,
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
                total_price=total_price,
                purchase_date=purchase_date,
                notes=notes
            )
            db.add(supply)
            db.commit()
            db.refresh(supply)
            return True, supply.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def update(self, supply_id, supply_name, supplier_id, quantity, unit, unit_price, total_price, purchase_date, notes):
        """Update an existing supply"""
        db = self._get_session()
        try:
            supply = db.query(Supply).filter(Supply.id == supply_id).first()
            if supply:
                supply.supply_name = supply_name
                supply.supplier_id = supplier_id
                supply.quantity = quantity
                supply.unit = unit
                supply.unit_price = unit_price
                supply.total_price = total_price
                supply.purchase_date = purchase_date
                supply.notes = notes
                supply.updated_at = datetime.now()
                db.commit()
                return True, "Insumo actualizado"
            return False, "Insumo no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete(self, supply_id):
        """Delete a supply"""
        db = self._get_session()
        try:
            supply = db.query(Supply).filter(Supply.id == supply_id).first()
            if supply:
                db.delete(supply)
                db.commit()
                return True, "Insumo eliminado"
            return False, "Insumo no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def search(self, term):
        """Search supplies by name or supplier"""
        db = self._get_session()
        try:
            supplies = db.query(Supply).join(Supplier).filter(
                (Supply.supply_name.ilike(f'%{term}%') |
                 Supplier.supplier_name.ilike(f'%{term}%'))
            ).order_by(Supply.purchase_date.desc()).all()
            return [
                {
                    'id': s.id,
                    'supply_name': s.supply_name,
                    'supplier_id': s.supplier_id,
                    'supplier_name': s.supplier.supplier_name if s.supplier else 'N/A',
                    'quantity': s.quantity,
                    'unit': s.unit,
                    'unit_price': s.unit_price,
                    'total_price': s.total_price,
                    'purchase_date': s.purchase_date,
                    'notes': s.notes
                }
                for s in supplies
            ]
        finally:
            db.close()

    def get_suppliers_list(self):
        """Get list of active suppliers for dropdown"""
        db = self._get_session()
        try:
            suppliers = db.query(Supplier).filter(Supplier.active == True).order_by(Supplier.supplier_name).all()
            return [(s.id, s.supplier_name) for s in suppliers]
        finally:
            db.close()


# Singleton instance
supply_provider = SupplyProvider()
