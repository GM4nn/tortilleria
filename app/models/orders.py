from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.data.database import Base


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=func.now())
    total = Column(Float, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    status = Column(String(50), default='pendiente')  # pendiente, completado, cancelado
    notes = Column(String(500), nullable=True)

    # Relationships
    order_details = relationship('OrderDetail', back_populates='order', cascade='all, delete-orphan')
    customer = relationship('Customer', backref='orders')

    def __repr__(self):
        return f"<Order(id={self.id}, date={self.date}, total={self.total}, customer_id={self.customer_id}, status={self.status})>"


class OrderDetail(Base):
    __tablename__ = 'order_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)  # Precio personalizado para este cliente
    subtotal = Column(Float, nullable=False)

    # Relationships
    order = relationship('Order', back_populates='order_details')
    product = relationship('Product', backref='order_details')

    def __repr__(self):
        return f"<OrderDetail(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"
