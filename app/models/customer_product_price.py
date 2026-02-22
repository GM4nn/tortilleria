from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.data.database import Base
from app.constants import mexico_now


class CustomerProductPrice(Base):
    __tablename__ = 'customer_product_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    custom_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=mexico_now)
    updated_at = Column(DateTime, default=mexico_now, onupdate=mexico_now)

    __table_args__ = (
        UniqueConstraint('customer_id', 'product_id', name='uq_customer_product_price'),
    )

    customer = relationship('Customer')
    product = relationship('Product')

    def __repr__(self):
        return f"<CustomerProductPrice(customer_id={self.customer_id}, product_id={self.product_id}, price={self.custom_price})>"
