from app.database import SessionLocal
from app.services.alert_service import seed_alerts


def run() -> int:
    db = SessionLocal()
    try:
        seed_alerts(db)
        return 1
    finally:
        db.close()
