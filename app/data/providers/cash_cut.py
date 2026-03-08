from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.cash_cut import CashCut
from app.models import Sale, Order
from app.data.database import get_db
from app.constants import mexico_now


def _day_range(d):
    """Returns (start_of_day, start_of_next_day) for datetime range queries.
    Portable across SQLite, PostgreSQL, MySQL."""
    start = datetime(d.year, d.month, d.day)
    return start, start + timedelta(days=1)


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
            day_start, day_end = _day_range(mexico_now().date())
            cut = db.query(CashCut).filter(
                CashCut.closed_at >= day_start,
                CashCut.closed_at < day_end,
            ).first()
            if cut:
                return {
                    'id': cut.id,
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

    def get_current_period_summary(self):
        db = get_db()
        try:
            day_start, day_end = _day_range(mexico_now().date())

            # Sales of today
            sales_result = db.query(
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total), 0.0)
            ).filter(
                Sale.date >= day_start,
                Sale.date < day_end,
            ).first()

            sales_count = sales_result[0] or 0
            sales_total = sales_result[1] or 0.0

            # Completed orders of today
            orders_result = db.query(
                func.count(Order.id),
                func.coalesce(func.sum(Order.total), 0.0)
            ).filter(
                Order.status == 'completado',
                Order.completed_at >= day_start,
                Order.completed_at < day_end,
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

    def get_all(self, offset=0, limit=None, filters=None):
        db = get_db()
        try:
            query = db.query(
                CashCut.id,
                CashCut.closed_at,
                CashCut.expected_total,
                CashCut.declared_cash,
                CashCut.declared_card,
                CashCut.declared_transfer,
                CashCut.declared_total,
                CashCut.difference,
                CashCut.sales_count,
                CashCut.orders_count,
            ).order_by(CashCut.closed_at.desc())

            if filters:
                for f in filters:
                    query = query.filter(f)

            if limit is not None:
                query = query.offset(offset).limit(limit)

            return query.all()
        finally:
            db.close()

    def get_count(self, filters=None):
        db = get_db()
        try:
            query = db.query(func.count(CashCut.id))
            if filters:
                for f in filters:
                    query = query.filter(f)
            return query.scalar() or 0
        finally:
            db.close()

    def build_date_range_filter(self, start_date, end_date):
        start_dt = datetime(start_date.year, start_date.month, start_date.day)
        end_dt = datetime(end_date.year, end_date.month, end_date.day) + timedelta(days=1)
        return [
            CashCut.closed_at >= start_dt,
            CashCut.closed_at < end_dt,
        ]

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
