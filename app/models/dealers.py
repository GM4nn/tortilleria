from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.data.database import Base
from app.constants import mexico_now


class Dealer(Base):
    __tablename__ = 'dealers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    pin = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=mexico_now)

    def __repr__(self):
        return f"<Dealer(id={self.id}, username='{self.username}', name='{self.name}')>"
