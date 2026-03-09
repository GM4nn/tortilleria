import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from app.constants import DB_NAME

# En .exe la DB se guarda junto al ejecutable, en desarrollo en la raíz del proyecto
_db_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else ''
DATABASE_URL = f"sqlite:///{os.path.join(_db_dir, DB_NAME)}.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker[Session](autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """
    Returns a new database session.
    The caller is responsible for closing it.
    """
    return SessionLocal()
