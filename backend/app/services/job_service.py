from __future__ import annotations

import time
from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import Alert, IngestionJobLog
from app.services.alert_service import create_alert, seed_alerts
from app.services.disaster_risk_engine import calculate_disaster_risk
from app.services.geospatial_service import ensure_geojson
from app.services.observation_service import persist_provider_records
from app.services.provider_service import (
    fetch_news_items,
    fetch_traffic_observations,
    fetch_weather_observations,
)


def run_job(db: Session, job_name: str, triggered_by: str = "system") -> dict[str, object]:
    job_map: dict[str, Callable[[], int]] = {
        "news": lambda: _fetch_and_persist(db, "news"),
        "weather": lambda: _fetch_and_persist(db, "weather"),
        "traffic": lambda: _fetch_and_persist(db, "traffic"),
        "risk": lambda: len(calculate_disaster_risk()),
        "alerts": lambda: _generate_alerts(db),
        "geospatial": lambda: _refresh_geojson(),
    }
    if job_name not in job_map:
        raise ValueError(f"Unsupported job: {job_name}")

    settings = get_settings()
    started_at = datetime.utcnow()
    log = IngestionJobLog(job_name=job_name, status="Running", started_at=started_at, triggered_by=triggered_by)
    db.add(log)
    db.commit()
    attempts = max(1, settings.job_max_retries + 1)
    try:
        records = 0
        for attempt in range(1, attempts + 1):
            try:
                records = job_map[job_name]()
                log.retry_count = attempt - 1
                break
            except Exception as exc:
                log.retry_count = attempt - 1
                if attempt >= attempts:
                    raise exc
                time.sleep(settings.job_retry_backoff_seconds)
        log.status = "Success"
        log.records_processed = records
    except Exception as exc:
        log.status = "Failed"
        log.error_message = str(exc)
        if settings.failure_alerts_enabled:
            _create_failure_alert(db, job_name, exc, triggered_by)
    log.completed_at = datetime.utcnow()
    log.duration_ms = int((log.completed_at - started_at).total_seconds() * 1000)
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
        "retry_count": log.retry_count,
        "duration_ms": log.duration_ms,
        "triggered_by": log.triggered_by,
    }


def _generate_alerts(db: Session) -> int:
    before = db.query(Alert).count()
    seed_alerts(db)
    return max(0, db.query(Alert).count() - before)


def _refresh_geojson() -> int:
    ensure_geojson()
    return 1


def _fetch_and_persist(db: Session, job_name: str) -> int:
    if job_name == "news":
        records = fetch_news_items()
    elif job_name == "weather":
        records = fetch_weather_observations()
    elif job_name == "traffic":
        records = fetch_traffic_observations()
    else:
        records = []
    return persist_provider_records(db, f"{job_name.title()}Job", job_name, records)


def _create_failure_alert(db: Session, job_name: str, exc: Exception, triggered_by: str) -> None:
    create_alert(
        db,
        {
            "title": f"Ingestion failure: {job_name}",
            "description": f"The {job_name} ingestion job failed after configured retries: {exc}",
            "district_id": "NCR01",
            "district_name": "Delhi NCT",
            "category": "Public Safety",
            "severity": "Medium",
            "priority": "P3",
            "assigned_department": "Platform Operations",
            "source": "CivicIQ Scheduler",
            "recommended_actions": [
                "Check provider credentials and rate limits.",
                "Review job logs and retry once provider status is healthy.",
            ],
        },
        actor=triggered_by,
    )
