from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.data.database import Base


class Supply(Base):
    """Modelo para representar un tipo de insumo (entidad única)"""
    __tablename__ = 'supplies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supply_name = Column(String(100), nullable=False, unique=True)  # Nombre del insumo (Maíz, Harina, etc.)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)  # Proveedor principal
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    supplier = relationship("Supplier", backref="supplies")
    purchases = relationship("SupplyPurchase", back_populates="supply", cascade="all, delete-orphan")
    consumptions = relationship("SupplyConsumption", back_populates="supply", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Supply(id={self.id}, name='{self.supply_name}')>"


class SupplyPurchase(Base):
    """Modelo para representar cada compra de un insumo"""
    __tablename__ = 'supply_purchases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supply_id = Column(Integer, ForeignKey('supplies.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)  # Proveedor de esta compra
    purchase_date = Column(Date, nullable=False, default=func.current_date())
    quantity = Column(Float, nullable=False)  # Cantidad comprada
    unit = Column(String(50), nullable=False)  # Unidad (kilos, litros, piezas, costales, etc.)
    unit_price = Column(Float, nullable=False)  # Precio por unidad
    total_price = Column(Float, nullable=False)  # Precio total
    initial_stock = Column(Float, nullable=False, default=0.0)  # Stock acumulado ANTES de esta compra (restante de compras anteriores)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    supply = relationship("Supply", back_populates="purchases")
    supplier = relationship("Supplier", backref="supply_purchases")

    def __repr__(self):
        return f"<SupplyPurchase(id={self.id}, supply_id={self.supply_id}, supplier_id={self.supplier_id}, date={self.purchase_date})>"


class SupplyConsumption(Base):
    """Modelo para registrar el consumo de insumos entre compras"""
    __tablename__ = 'supply_consumptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supply_id = Column(Integer, ForeignKey('supplies.id'), nullable=False)
    start_date = Column(Date, nullable=False)  # Fecha de inicio del período
    end_date = Column(Date, nullable=False)  # Fecha de fin del período
    quantity_consumed = Column(Float, nullable=False)  # Cantidad consumida
    quantity_remaining = Column(Float, nullable=False)  # Cantidad restante
    unit = Column(String(50), nullable=False)  # Unidad de medida
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    supply = relationship("Supply", back_populates="consumptions")

    def __repr__(self):
        return f"<SupplyConsumption(id={self.id}, supply_id={self.supply_id}, consumed={self.quantity_consumed})>"
