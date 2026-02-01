from app.data.database import get_db
from app.models import IAConfig


class IAProvider:

    def get_api_key(self):
        """Get the stored API key (only one record exists)"""
        db = get_db()
        try:
            record = db.query(IAConfig).first()
            if record:
                return record.api_key
            return None
        finally:
            db.close()

    def save_api_key(self, key: str):
        """Save or update the API key (always one record)"""
        db = get_db()
        try:
            record = db.query(IAConfig).first()
            if record:
                record.api_key = key
            else:
                record = IAConfig(api_key=key)
                db.add(record)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()


# Singleton instance
ia_provider = IAProvider()
