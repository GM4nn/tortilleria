from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database import Base


class SaleDetail(Base):
    __tablename__ = 'sales_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    # Relationships
    sale = relationship('Sale', back_populates='sales_details')
    product = relationship('Product', back_populates='sales_details')

    def __repr__(self):
        return f"<SaleDetail(id={self.id}, sale_id={self.sale_id}, product_id={self.product_id})>"
