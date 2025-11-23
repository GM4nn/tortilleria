from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.data.database import Base


class Supply(Base):
    __tablename__ = 'supplies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supply_name = Column(String(100), nullable=False)  # Nombre del insumo (Maíz, Harina, etc.)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    quantity = Column(Float, nullable=False)  # Cantidad comprada
    unit = Column(String(50), nullable=False)  # Unidad (kilos, litros, piezas, etc.)
    unit_price = Column(Float, nullable=False)  # Precio por unidad
    total_price = Column(Float, nullable=False)  # Precio total
    purchase_date = Column(DateTime, default=func.now())
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship with Supplier
    supplier = relationship("Supplier", backref="supplies")

    def __repr__(self):
        return f"<Supply(id={self.id}, name='{self.supply_name}', quantity={self.quantity})>"
