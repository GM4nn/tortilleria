from app.models import Supply, SupplyPurchase, Supplier
from sqlalchemy.orm import joinedload
from app.data.database import get_db
from datetime import datetime, date
from app.constants import mexico_now


class SupplyProvider:


    # ===== SUPPLIES (Insumos) =====

    def get_all_supplies(self):
        """Get all unique supplies with their supplier info"""

        db = get_db()

        try:
            supplies = db.query(Supply).options(joinedload(Supply.supplier)).all()
            return [
                {
                    'id': s.id,
                    'supply_name': s.supply_name,
                    'supplier_id': s.supplier_id,
                    'supplier_name': s.supplier.supplier_name if s.supplier else 'N/A',
                    'unit': s.unit,
                    'created_at': s.created_at,
                    'updated_at': s.updated_at
                }
                for s in supplies
            ]
        finally:
            db.close()

    def get_supply_by_id(self, supply_id):
        """Get a supply by ID with all its purchases"""

        db = get_db()

        try:
            supply = db.query(Supply).options(
                joinedload(Supply.supplier),
                joinedload(Supply.purchases).joinedload(SupplyPurchase.supplier),
            ).filter(Supply.id == supply_id).first()

            if supply:
                return {
                    'id': supply.id,
                    'supply_name': supply.supply_name,
                    'supplier_id': supply.supplier_id,
                    'supplier_name': supply.supplier.supplier_name if supply.supplier else 'N/A',
                    'unit': supply.unit,
                    'purchases': sorted(
                        [
                            {
                                'id': p.id,
                                'purchase_date': p.purchase_date,
                                'quantity': p.quantity,
                                'unit': p.unit,
                                'unit_price': p.unit_price,
                                'total_price': p.total_price,
                                'remaining': p.remaining,
                                'supplier_id': p.supplier_id,
                                'supplier_name': p.supplier.supplier_name if p.supplier else 'N/A',
                                'notes': p.notes
                            }
                            for p in supply.purchases
                        ],
                        key=lambda x: x['purchase_date'], reverse=True
                    ),
                }
            return
        finally:
            db.close()

    def get_supply_by_name(self, supply_name):

        db = get_db()

        try:
            supply = db.query(Supply).filter(Supply.supply_name == supply_name).first()
            if supply:
                return supply.id
            return
        finally:
            db.close()

    def create_supply(self, supply_name, supplier_id, unit):

        db = get_db()

        try:
            supply = Supply(
                supply_name=supply_name,
                supplier_id=supplier_id,
                unit=unit
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

    def update_supply(self, supply_id, supply_name, supplier_id, unit):

        db = get_db()
        try:
            supply = db.query(Supply).filter(Supply.id == supply_id).first()
            if supply:
                supply.supply_name = supply_name
                supply.supplier_id = supplier_id
                supply.unit = unit
                supply.updated_at = mexico_now()
                db.commit()
                return True, "Insumo actualizado"
            return False, "Insumo no encontrado"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete_supply(self, supply_id):
        """Delete a supply and all its purchases (cascade)"""
        db = get_db()

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

        db = get_db()

        try:
            purchases = db.query(SupplyPurchase).options(
                joinedload(SupplyPurchase.supplier)
            ).filter(
                SupplyPurchase.supply_id == supply_id
            ).order_by(
                SupplyPurchase.purchase_date.desc()
            ).all()

            return [
                {
                    'id': p.id,
                    'purchase_date': p.purchase_date,
                    'quantity': p.quantity,
                    'unit': p.unit,
                    'unit_price': p.unit_price,
                    'total_price': p.total_price,
                    'remaining': p.remaining,
                    'supplier_id': p.supplier_id,
                    'supplier_name': p.supplier.supplier_name if p.supplier else 'N/A',
                    'notes': p.notes
                }
                for p in purchases
            ]
        finally:
            db.close()

    def get_purchases_paginated(self, supply_id, offset=0, limit=10):
        """Get purchases for a supply with server-side pagination"""
        db = get_db()
        try:
            purchases = db.query(SupplyPurchase).options(
                joinedload(SupplyPurchase.supplier)
            ).filter(
                SupplyPurchase.supply_id == supply_id
            ).order_by(
                SupplyPurchase.purchase_date.desc()
            ).offset(offset).limit(limit).all()

            return [
                {
                    'id': p.id,
                    'purchase_date': p.purchase_date,
                    'quantity': p.quantity,
                    'unit': p.unit,
                    'unit_price': p.unit_price,
                    'total_price': p.total_price,
                    'remaining': p.remaining,
                    'supplier_id': p.supplier_id,
                    'supplier_name': p.supplier.supplier_name if p.supplier else 'N/A',
                    'notes': p.notes
                }
                for p in purchases
            ]
        finally:
            db.close()

    def count_purchases(self, supply_id):
        """Count total purchases for a supply"""
        db = get_db()
        try:
            return db.query(SupplyPurchase).filter(
                SupplyPurchase.supply_id == supply_id
            ).count()
        finally:
            db.close()

    def get_periods_paginated(self, supply_id, offset=0, limit=10):
        """Get consumption periods (derived from consecutive purchases) with pagination.
        Each period needs 2 consecutive purchases, so we fetch limit+1 purchases at the given offset.
        """
        db = get_db()
        try:
            purchases = db.query(SupplyPurchase).options(
                joinedload(SupplyPurchase.supplier)
            ).filter(
                SupplyPurchase.supply_id == supply_id
            ).order_by(
                SupplyPurchase.purchase_date.desc()
            ).offset(offset).limit(limit + 1).all()

            periods = []
            for i in range(len(purchases) - 1):
                curr = purchases[i]
                prev = purchases[i + 1]
                prev_remaining = prev.remaining or 0.0
                total_available = prev_remaining + prev.quantity
                curr_remaining = curr.remaining or 0.0
                consumed = max(0, total_available - curr_remaining)

                periods.append({
                    'start_date': prev.purchase_date,
                    'end_date': curr.purchase_date,
                    'quantity': prev.quantity,
                    'unit': prev.unit,
                    'prev_remaining': prev_remaining,
                    'total_available': total_available,
                    'consumed': consumed,
                    'remaining': curr_remaining,
                })

            print(f"limit {limit} offset {offset}")

            return periods
        finally:
            db.close()

    def count_periods(self, supply_id):
        """Count total periods (= total purchases - 1)"""
        count = self.count_purchases(supply_id)
        return max(0, count - 1)

    def has_previous_purchases(self, supply_id):
        """Check if a supply has previous purchases"""
        db = get_db()

        try:
            count = db.query(SupplyPurchase).filter(
                SupplyPurchase.supply_id == supply_id
            ).count()
            return count > 0

        finally:
            db.close()

    def add_purchase(self, supply_id, supplier_id, purchase_date, quantity, unit, unit_price, total_price, remaining=0.0, notes=None):
        """Add a new purchase for a supply"""

        db = get_db()

        try:
            purchase = SupplyPurchase(
                supply_id=supply_id,
                supplier_id=supplier_id,
                purchase_date=purchase_date if isinstance(purchase_date, date) else datetime.strptime(purchase_date, "%Y-%m-%d").date(),
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
                total_price=total_price,
                remaining=remaining,
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

    def update_purchase(self, purchase_id, supplier_id, purchase_date, quantity, unit, unit_price, total_price, remaining=None, notes=None):

        db = get_db()

        try:
            purchase = db.query(SupplyPurchase).filter(SupplyPurchase.id == purchase_id).first()

            if purchase:
                purchase.supplier_id = supplier_id
                purchase.purchase_date = purchase_date if isinstance(purchase_date, date) else datetime.strptime(purchase_date, "%Y-%m-%d").date()
                purchase.quantity = quantity
                purchase.unit = unit
                purchase.unit_price = unit_price
                purchase.total_price = total_price
                if remaining is not None:
                    purchase.remaining = remaining
                purchase.notes = notes
                purchase.updated_at = mexico_now()
                db.commit()

                return True, "Compra actualizada"

            return False, "Compra no encontrada"
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def delete_purchase(self, purchase_id):

        db = get_db()

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

    # ===== HELPERS =====

    def get_current_stock(self, supply_id):
        """Stock actual = remaining + quantity de la ultima compra"""
        db = get_db()
        try:
            last_purchase = db.query(SupplyPurchase).filter(
                SupplyPurchase.supply_id == supply_id
            ).order_by(SupplyPurchase.purchase_date.desc()).first()

            if not last_purchase:
                return 0.0
            return last_purchase.remaining + last_purchase.quantity
        finally:
            db.close()

    def get_suppliers_list(self):
        """Get list of active suppliers for dropdown"""

        db = get_db()

        try:

            suppliers = db.query(Supplier).filter(Supplier.active == True).order_by(Supplier.supplier_name).all()
            return [(s.id, s.supplier_name) for s in suppliers]

        finally:
            db.close()

    def search_supplies(self, term):
        """Search supplies by name"""

        db = get_db()

        try:

            supplies = db.query(Supply).join(Supplier).filter(
                (
                    Supply.supply_name.ilike(f'%{term}%') |
                    Supplier.supplier_name.ilike(f'%{term}%')
                )
            ).all()

            return [
                {
                    'id': s.id,
                    'supply_name': s.supply_name,
                    'supplier_id': s.supplier_id,
                    'supplier_name': s.supplier.supplier_name if s.supplier else 'N/A',
                    'unit': s.unit,
                }
                for s in supplies
            ]
        finally:
            db.close()


# Singleton instance
supply_provider = SupplyProvider()
