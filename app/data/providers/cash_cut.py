from sqlalchemy import func
from app.models.cash_cut import CashCut
from app.models import Sale, Order
from app.data.database import get_db
from app.constants import mexico_now


class CashCutProvider:

    def get_last_cut(self):
        db = get_db()
        try:
            cut = db.query(CashCut).order_by(CashCut.closed_at.desc()).first()
            if cut:
                return {
                    'id': cut.id,
                    'opened_at': cut.opened_at,
                    'closed_at': cut.closed_at,
                    'expected_total': cut.expected_total,
                    'declared_total': cut.declared_total,
                    'difference': cut.difference,
                }
            return None
        finally:
            db.close()

    def get_today_cut(self):
        db = get_db()
        try:
            today_str = mexico_now().date().isoformat()
            cut = db.query(CashCut).filter(
                func.date(CashCut.closed_at) == today_str
            ).first()
            if cut:
                return {
                    'id': cut.id,
                    'closed_at': cut.closed_at,
                    'declared_total': cut.declared_total,
                }
            return None
        finally:
            db.close()

    def get_current_period_summary(self):
        db = get_db()
        try:
            today_str = mexico_now().date().isoformat()

            # Sales of today
            sales_result = db.query(
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total), 0.0)
            ).filter(
                func.date(Sale.date) == today_str
            ).first()

            sales_count = sales_result[0] or 0
            sales_total = sales_result[1] or 0.0

            # Completed orders of today
            orders_result = db.query(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total), 0.0)
            ).filter(
                Order.status == 'completado',
                func.date(Order.completed_at) == today_str
            ).first()

            orders_count = orders_result[0] or 0
            orders_total = orders_result[1] or 0.0

            expected_total = sales_total + orders_total

            return {
                'today': mexico_now().date(),
                'sales_count': sales_count,
                'sales_total': sales_total,
                'orders_count': orders_count,
                'orders_total': orders_total,
                'expected_total': expected_total,
            }
        finally:
            db.close()

    def save(self, data):
        db = get_db()
        try:
            cut = CashCut(
                opened_at=data['opened_at'],
                closed_at=mexico_now(),
                sales_count=data['sales_count'],
                orders_count=data['orders_count'],
                sales_total=data['sales_total'],
                orders_total=data['orders_total'],
                expected_total=data['expected_total'],
                declared_cash=data['declared_cash'],
                declared_card=data['declared_card'],
                declared_transfer=data['declared_transfer'],
                declared_total=data['declared_total'],
                difference=data['difference'],
                notes=data.get('notes'),
            )
            db.add(cut)
            db.commit()
            return True, cut.id
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally:
            db.close()

    def get_all(self, offset=0, limit=None):
        db = get_db()
        try:
            query = db.query(
                CashCut.id,
                CashCut.closed_at,
                CashCut.expected_total,
                CashCut.declared_total,
                CashCut.difference,
                CashCut.sales_count,
                CashCut.orders_count,
            ).order_by(CashCut.closed_at.desc())

            if limit is not None:
                query = query.offset(offset).limit(limit)

            return query.all()
        finally:
            db.close()

    def get_count(self):
        db = get_db()
        try:
            return db.query(func.count(CashCut.id)).scalar() or 0
        finally:
            db.close()

    def get_by_id(self, cut_id):
        db = get_db()
        try:
            cut = db.query(CashCut).filter(CashCut.id == cut_id).first()
            if cut:
                return {
                    'id': cut.id,
                    'opened_at': cut.opened_at,
                    'closed_at': cut.closed_at,
                    'sales_count': cut.sales_count,
                    'orders_count': cut.orders_count,
                    'sales_total': cut.sales_total,
                    'orders_total': cut.orders_total,
                    'expected_total': cut.expected_total,
                    'declared_cash': cut.declared_cash,
                    'declared_card': cut.declared_card,
                    'declared_transfer': cut.declared_transfer,
                    'declared_total': cut.declared_total,
                    'difference': cut.difference,
                    'notes': cut.notes,
                }
            return None
        finally:
            db.close()


cash_cut_provider = CashCutProvider()
