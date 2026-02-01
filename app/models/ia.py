from sqlalchemy import Column, Integer, String
from app.data.database import Base


class IAConfig(Base):
    __tablename__ = 'ia_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String, nullable=False)

    def __repr__(self):
        return f"<IAConfig(id={self.id})>"
