from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.data.database import Base
from app.constants import mexico_now


class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name = Column(String(100), nullable=False)
    contact_name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    city = Column(String(100))
    product_type = Column(String(100))  # Tipo de producto que provee (Maíz, Harina, Insumos, etc.)
    notes = Column(Text)
    created_at = Column(DateTime, default=mexico_now)
    updated_at = Column(DateTime, default=mexico_now, onupdate=mexico_now)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.supplier_name}')>"
