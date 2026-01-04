
from sqlalchemy import text
from typing import Any, Dict
from app.data.database import SessionLocal
from app.constants import DANGEROUS_KEYWORDS


class DatabaseTool:
    """Tool that allows AI to execute SQL queries directly"""

    def __init__(self):
        self.allowed_operations = ['SELECT']  # Only read operations for safety


    def validate_sql(self, sql: str) -> tuple[bool, str]:
        """
        Validate SQL query for security
        Returns (is_valid, error_message)
        """
    
        sql_upper = sql.upper().strip()

        # Only allow SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Solo se permiten consultas SELECT"

        # Block dangerous keywords
        for keyword in DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"Palabra clave peligrosa detectada: {keyword}"

        # Must have FROM clause
        if 'FROM' not in sql_upper:
            return False, "La consulta debe tener una cláusula FROM"

        return True, ""

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        """
        # Validate first
        is_valid, error_msg = self.validate_sql(sql)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "query": sql
            }

        db = SessionLocal()
        try:
            # Execute query
            result = db.execute(text(sql))

            # Fetch results
            rows = result.fetchall()

            # Convert to list of dicts
            if rows:
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]
            else:
                data = []

            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "query": sql
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": sql
            }
        finally:
            db.close()