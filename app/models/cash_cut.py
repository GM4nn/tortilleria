from sqlalchemy import Column, Integer, Float, String, DateTime
from app.data.database import Base
from app.constants import mexico_now


class CashCut(Base):
    __tablename__ = 'cash_cuts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, default=mexico_now)
    sales_count = Column(Integer, default=0)
    orders_count = Column(Integer, default=0)
    sales_total = Column(Float, default=0.0)
    orders_total = Column(Float, default=0.0)
    expected_total = Column(Float, default=0.0)
    declared_cash = Column(Float, default=0.0)
    declared_card = Column(Float, default=0.0)
    declared_transfer = Column(Float, default=0.0)
    declared_total = Column(Float, default=0.0)
    difference = Column(Float, default=0.0)
    notes = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<CashCut(id={self.id}, closed_at={self.closed_at}, expected={self.expected_total}, declared={self.declared_total})>"
