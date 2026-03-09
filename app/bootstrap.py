"""
Bootstrap: configuración inicial para ejecutar la app como .exe o en desarrollo.
Se llama UNA vez al inicio desde main.py.
"""

import sys
import os


def init():
    """Configura el entorno antes de iniciar la app."""
    if getattr(sys, 'frozen', False):
        # PyInstaller: los recursos (CSVs, logo, etc.) están en _MEIPASS
        os.chdir(sys._MEIPASS)

    # Crear tablas si la DB es nueva (primer inicio o instalación fresca)
    from app.data.database import Base, engine
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
