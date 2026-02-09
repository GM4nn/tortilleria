from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.data.database import Base
from app.constants import mexico_now


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    customer_direction = Column(String)
    customer_category = Column(String)
    customer_photo = Column(String)
    customer_phone = Column(String)
    created_at = Column(DateTime, default=mexico_now)
    updated_at = Column(DateTime, default=mexico_now, onupdate=mexico_now)
    active = Column(Boolean, default=True)
    active2 = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.customer_name}')>"
