from app.database import SessionLocal
from app.services.geospatial_provider import reload_boundaries


def run() -> int:
    db = SessionLocal()
    try:
        return len(reload_boundaries(db)["sources"])
    finally:
        db.close()
