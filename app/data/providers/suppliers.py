from sqlalchemy.orm import Session
from app.data.database import SessionLocal
from app.models import Supplier
from datetime import datetime


class SupplierProvider:
    """Provider para operaciones CRUD de proveedores"""

    def _get_session(self) -> Session:
        """Get a new database session"""
        return SessionLocal()

    def get_all(self):
        """Get all active suppliers"""
        db = self._get_session()
        try:
            suppliers = db.query(Supplier).filter(Supplier.active == True).order_by(Supplier.supplier_name).all()
            return [
                (s.id, s.supplier_name, s.contact_name, s.phone, s.email,
                 s.address, s.city, s.product_type, s.notes, s.created_at, s.updated_at)
                for s in suppliers
            ]
        finally:
            db.close()

    def get_by_id(self, supplier_id):
        """Get a supplier by ID"""
        db = self._get_session()
        try:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id, Supplier.active == True).first()
            if supplier:
                return (supplier.id, supplier.supplier_name, supplier.contact_name, supplier.phone,
                        supplier.email, supplier.address, supplier.city, supplier.product_type,
                        supplier.notes, supplier.created_at, supplier.updated_at)
            return None
        finally:
            db.close()

    def add(self, name, contact_name, phone, email, address, city, product_type, notes):
        """Add a new supplier"""
        db = self._get_session()
        try:
            supplier = Supplier(
                supplier_name=name,
                contact_name=contact_name,
                phone=phone,
                email=email,
                address=address,
                city=city,
                product_type=product_type,
                notes=notes
            )
            db.add(supplier)
            db.commit()
            db.refresh(supplier)
            return True, supplier.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def update(self, supplier_id, name, contact_name, phone, email, address, city, product_type, notes):
        """Update an existing supplier"""
        db = self._get_session()
        try:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                supplier.supplier_name = name
                supplier.contact_name = contact_name
                supplier.phone = phone
                supplier.email = email
                supplier.address = address
                supplier.city = city
                supplier.product_type = product_type
                supplier.notes = notes
                supplier.updated_at = datetime.now()
                db.commit()
                return True, "Proveedor actualizado"
            return False, "Proveedor no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete(self, supplier_id):
        """Soft delete a supplier (set active to False)"""
        db = self._get_session()
        try:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                supplier.active = False
                db.commit()
                return True, "Proveedor eliminado"
            return False, "Proveedor no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def search(self, term):
        """Search suppliers by name, contact or product type"""
        db = self._get_session()
        try:
            suppliers = db.query(Supplier).filter(
                Supplier.active == True,
                (Supplier.supplier_name.ilike(f'%{term}%') |
                 Supplier.contact_name.ilike(f'%{term}%') |
                 Supplier.product_type.ilike(f'%{term}%'))
            ).order_by(Supplier.supplier_name).all()
            return [
                (s.id, s.supplier_name, s.contact_name, s.phone, s.email,
                 s.address, s.city, s.product_type, s.notes, s.created_at, s.updated_at)
                for s in suppliers
            ]
        finally:
            db.close()


# Singleton instance
supplier_provider = SupplierProvider()
