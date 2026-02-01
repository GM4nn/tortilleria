from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from app.data.database import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, default='🍴')
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)

    # Relationship
    sales_details = relationship('SaleDetail', back_populates='product')

    def __repr__(self):
        return f"<Product(id={self.id}, icon='{self.icon}', name='{self.name}', price={self.price})>"
