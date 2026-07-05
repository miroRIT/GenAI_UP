from __future__ import annotations

from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from app.models.db_models import IngestionJobLog
from app.services.alert_service import seed_alerts
from app.services.disaster_risk_engine import calculate_disaster_risk
from app.services.geospatial_service import ensure_geojson
from app.services.provider_service import (
    fetch_news_items,
    fetch_traffic_observations,
    fetch_weather_observations,
)


def run_job(db: Session, job_name: str) -> dict[str, object]:
    job_map: dict[str, Callable[[], int]] = {
        "news": lambda: len(fetch_news_items()),
        "weather": lambda: len(fetch_weather_observations()),
        "traffic": lambda: len(fetch_traffic_observations()),
        "risk": lambda: len(calculate_disaster_risk()),
        "alerts": lambda: _generate_alerts(db),
        "geospatial": lambda: _refresh_geojson(),
    }
    if job_name not in job_map:
        raise ValueError(f"Unsupported job: {job_name}")

    log = IngestionJobLog(job_name=job_name, status="Running", started_at=datetime.utcnow())
    db.add(log)
    db.commit()
    try:
        records = job_map[job_name]()
        log.status = "Success"
        log.records_processed = records
    except Exception as exc:
        log.status = "Failed"
        log.error_message = str(exc)
    log.completed_at = datetime.utcnow()
    db.commit()
    return serialize_job_log(log)


def job_status(db: Session) -> list[dict[str, object]]:
    logs = db.query(IngestionJobLog).order_by(IngestionJobLog.started_at.desc()).limit(50).all()
    return [serialize_job_log(log) for log in logs]


def serialize_job_log(log: IngestionJobLog) -> dict[str, object]:
    return {
        "id": log.id,
        "job_name": log.job_name,
        "status": log.status,
        "started_at": log.started_at.isoformat(),
        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        "records_processed": log.records_processed,
        "error_message": log.error_message,
    }


def _generate_alerts(db: Session) -> int:
    before = len(db.identity_map)
    seed_alerts(db)
    return max(0, len(db.identity_map) - before)


def _refresh_geojson() -> int:
    ensure_geojson()
    return 1
