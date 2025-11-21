from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.data.database import Base


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=func.now())
    total = Column(Float, nullable=False)

    # Relationship
    sales_details = relationship('SaleDetail', back_populates='sale', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Sale(id={self.id}, date={self.date}, total={self.total})>"
