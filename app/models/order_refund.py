from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database import Base
from app.constants import mexico_now


class OrderRefund(Base):
    __tablename__ = 'order_refunds'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    comments = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=mexico_now)

    # Relationships
    order = relationship('Order', backref='refunds')
    product = relationship('Product', backref='order_refunds')

    def __repr__(self):
        return f"<OrderRefund(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"
