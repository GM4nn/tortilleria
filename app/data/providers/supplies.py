from sqlalchemy.orm import Session, joinedload
from app.data.database import SessionLocal
from app.models import Supply, SupplyPurchase, SupplyConsumption, Supplier
from datetime import datetime, date


class SupplyProvider:
    """Provider para operaciones CRUD de insumos, compras y consumos"""

    def _get_session(self) -> Session:
        """Get a new database session"""
        return SessionLocal()

    # ===== SUPPLIES (Insumos) =====

    def get_all_supplies(self):
        """Get all unique supplies with their supplier info"""
        db = self._get_session()
        try:
            supplies = db.query(Supply).options(joinedload(Supply.supplier)).all()
            return [
                {
                    'id': s.id,
                    'supply_name': s.supply_name,
                    'supplier_id': s.supplier_id,
                    'supplier_name': s.supplier.supplier_name if s.supplier else 'N/A',
                    'created_at': s.created_at,
                    'updated_at': s.updated_at
                }
                for s in supplies
            ]
        finally:
            db.close()

    def get_supply_by_id(self, supply_id):
        """Get a supply by ID with all its purchases and consumptions"""
        db = self._get_session()
        try:
            supply = db.query(Supply).options(
                joinedload(Supply.supplier),
                joinedload(Supply.purchases).joinedload(SupplyPurchase.supplier),
                joinedload(Supply.consumptions)
            ).filter(Supply.id == supply_id).first()

            if supply:
                return {
                    'id': supply.id,
                    'supply_name': supply.supply_name,
                    'supplier_id': supply.supplier_id,
                    'supplier_name': supply.supplier.supplier_name if supply.supplier else 'N/A',
                    'purchases': sorted([
                        {
                            'id': p.id,
                            'purchase_date': p.purchase_date,
                            'quantity': p.quantity,
                            'unit': p.unit,
                            'unit_price': p.unit_price,
                            'total_price': p.total_price,
                            'supplier_id': p.supplier_id,
                            'supplier_name': p.supplier.supplier_name if p.supplier else 'N/A',
                            'notes': p.notes
                        }
                        for p in supply.purchases
                    ], key=lambda x: x['purchase_date'], reverse=True),
                    'consumptions': sorted([
                        {
                            'id': c.id,
                            'start_date': c.start_date,
                            'end_date': c.end_date,
                            'quantity_consumed': c.quantity_consumed,
                            'quantity_remaining': c.quantity_remaining,
                            'unit': c.unit,
                            'notes': c.notes
                        }
                        for c in supply.consumptions
                    ], key=lambda x: x['end_date'], reverse=True)
                }
            return None
        finally:
            db.close()

    def get_supply_by_name(self, supply_name):
        """Get a supply by name"""
        db = self._get_session()
        try:
            supply = db.query(Supply).filter(Supply.supply_name == supply_name).first()
            if supply:
                return supply.id
            return None
        finally:
            db.close()

    def create_supply(self, supply_name, supplier_id):
        """Create a new supply (insumo único)"""
        db = self._get_session()
        try:
            supply = Supply(
                supply_name=supply_name,
                supplier_id=supplier_id
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

    def update_supply(self, supply_id, supply_name, supplier_id):
        """Update a supply"""
        db = self._get_session()
        try:
            supply = db.query(Supply).filter(Supply.id == supply_id).first()
            if supply:
                supply.supply_name = supply_name
                supply.supplier_id = supplier_id
                supply.updated_at = datetime.now()
                db.commit()
                return True, "Insumo actualizado"
            return False, "Insumo no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete_supply(self, supply_id):
        """Delete a supply (and all its purchases and consumptions due to cascade)"""
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

    # ===== PURCHASES (Compras) =====

    def get_purchases_by_supply(self, supply_id):
        """Get all purchases for a specific supply"""
        db = self._get_session()
        try:
            purchases = db.query(SupplyPurchase).options(
                joinedload(SupplyPurchase.supplier)
            ).filter(
                SupplyPurchase.supply_id == supply_id
            ).order_by(SupplyPurchase.purchase_date.desc()).all()

            return [
                {
                    'id': p.id,
                    'purchase_date': p.purchase_date,
                    'quantity': p.quantity,
                    'unit': p.unit,
                    'unit_price': p.unit_price,
                    'total_price': p.total_price,
                    'supplier_id': p.supplier_id,
                    'supplier_name': p.supplier.supplier_name if p.supplier else 'N/A',
                    'notes': p.notes
                }
                for p in purchases
            ]
        finally:
            db.close()

    def has_previous_purchases(self, supply_id):
        """Check if a supply has previous purchases"""
        db = self._get_session()
        try:
            count = db.query(SupplyPurchase).filter(
                SupplyPurchase.supply_id == supply_id
            ).count()
            return count > 0
        finally:
            db.close()

    def add_purchase(self, supply_id, supplier_id, purchase_date, quantity, unit, unit_price, total_price, notes=None):
        """Add a new purchase for a supply"""
        db = self._get_session()
        try:
            purchase = SupplyPurchase(
                supply_id=supply_id,
                supplier_id=supplier_id,
                purchase_date=purchase_date if isinstance(purchase_date, date) else datetime.strptime(purchase_date, "%Y-%m-%d").date(),
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
                total_price=total_price,
                notes=notes
            )
            db.add(purchase)
            db.commit()
            db.refresh(purchase)
            return True, purchase.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def update_purchase(self, purchase_id, supplier_id, purchase_date, quantity, unit, unit_price, total_price, notes=None):
        """Update an existing purchase"""
        db = self._get_session()
        try:
            purchase = db.query(SupplyPurchase).filter(SupplyPurchase.id == purchase_id).first()
            if purchase:
                purchase.supplier_id = supplier_id
                purchase.purchase_date = purchase_date if isinstance(purchase_date, date) else datetime.strptime(purchase_date, "%Y-%m-%d").date()
                purchase.quantity = quantity
                purchase.unit = unit
                purchase.unit_price = unit_price
                purchase.total_price = total_price
                purchase.notes = notes
                purchase.updated_at = datetime.now()
                db.commit()
                return True, "Compra actualizada"
            return False, "Compra no encontrada"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete_purchase(self, purchase_id):
        """Delete a purchase"""
        db = self._get_session()
        try:
            purchase = db.query(SupplyPurchase).filter(SupplyPurchase.id == purchase_id).first()
            if purchase:
                db.delete(purchase)
                db.commit()
                return True, "Compra eliminada"
            return False, "Compra no encontrada"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    # ===== CONSUMPTIONS (Consumos) =====

    def get_consumptions_by_supply(self, supply_id):
        """Get all consumptions for a specific supply"""
        db = self._get_session()
        try:
            consumptions = db.query(SupplyConsumption).filter(
                SupplyConsumption.supply_id == supply_id
            ).order_by(SupplyConsumption.end_date.desc()).all()

            return [
                {
                    'id': c.id,
                    'start_date': c.start_date,
                    'end_date': c.end_date,
                    'quantity_consumed': c.quantity_consumed,
                    'quantity_remaining': c.quantity_remaining,
                    'unit': c.unit,
                    'notes': c.notes
                }
                for c in consumptions
            ]
        finally:
            db.close()

    def add_consumption(self, supply_id, start_date, end_date, quantity_consumed, quantity_remaining, unit, notes=None):
        """Add a consumption record"""
        db = self._get_session()
        try:
            consumption = SupplyConsumption(
                supply_id=supply_id,
                start_date=start_date if isinstance(start_date, date) else datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=end_date if isinstance(end_date, date) else datetime.strptime(end_date, "%Y-%m-%d").date(),
                quantity_consumed=quantity_consumed,
                quantity_remaining=quantity_remaining,
                unit=unit,
                notes=notes
            )
            db.add(consumption)
            db.commit()
            db.refresh(consumption)
            return True, consumption.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    # ===== HELPERS =====

    def get_suppliers_list(self):
        """Get list of active suppliers for dropdown"""
        db = self._get_session()
        try:
            suppliers = db.query(Supplier).filter(Supplier.active == True).order_by(Supplier.supplier_name).all()
            return [(s.id, s.supplier_name) for s in suppliers]
        finally:
            db.close()

    def search_supplies(self, term):
        """Search supplies by name"""
        db = self._get_session()
        try:
            supplies = db.query(Supply).join(Supplier).filter(
                (Supply.supply_name.ilike(f'%{term}%') |
                 Supplier.supplier_name.ilike(f'%{term}%'))
            ).all()
            return [
                {
                    'id': s.id,
                    'supply_name': s.supply_name,
                    'supplier_id': s.supplier_id,
                    'supplier_name': s.supplier.supplier_name if s.supplier else 'N/A',
                }
                for s in supplies
            ]
        finally:
            db.close()


# Singleton instance
supply_provider = SupplyProvider()
