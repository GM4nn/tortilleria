"""
Database Manager - Now using SQLAlchemy ORM

This module provides backward compatibility by re-exporting
the SQLAlchemy-based DatabaseManager.

Migration completed: sqlite3 -> SQLAlchemy + Alembic
"""

from app.data.db_sqlalchemy import DatabaseManager

__all__ = ['DatabaseManager']