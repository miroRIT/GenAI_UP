from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import (
    AQIObservation,
    NewsObservation,
    ProviderObservation,
    TrafficObservation,
    WeatherObservation,
)


def persist_provider_records(
    db: Session,
    provider_name: str,
    provider_type: str,
    records: list[dict[str, Any]],
) -> int:
    count = 0
    for record in records:
        raw = ProviderObservation(
            provider_name=provider_name,
            provider_type=provider_type,
            district_id=str(record.get("district_id", "")),
            district_name=str(record.get("district_name", "")),
            observed_at=_parse_datetime(record.get("published_at") or record.get("observed_at")),
            source_url=str(record.get("url", "")),
            raw_payload_json=json.dumps(record, default=str),
            normalized_payload_json=json.dumps(record, default=str),
            confidence=float(record.get("confidence", 0.65)),
        )
        db.add(raw)
        db.flush()
        if provider_type == "weather":
            db.add(
                WeatherObservation(
                    provider_name=provider_name,
                    district_id=raw.district_id,
                    observed_at=raw.observed_at,
                    temperature=float(record.get("temperature", 0)),
                    feels_like=float(record.get("feels_like", 0)),
                    humidity=float(record.get("humidity", 0)),
                    rainfall_mm=float(record.get("rainfall_mm", record.get("rainfall", 0))),
                    wind_speed=float(record.get("wind_speed", 0)),
                    condition=str(record.get("weather_condition", record.get("condition", ""))),
                    heat_index=float(record.get("heat_index", 0)),
                    forecast_date=str(record.get("forecast", [{}])[0].get("date", "") if record.get("forecast") else ""),
                    raw_observation_id=raw.id,
                )
            )
        elif provider_type == "traffic":
            db.add(
                TrafficObservation(
                    provider_name=provider_name,
                    district_id=raw.district_id,
                    observed_at=raw.observed_at,
                    route_name=str(record.get("affected_route_name", record.get("route_name", ""))),
                    congestion_level=float(record.get("congestion_level", 0)),
                    average_speed_kmph=float(record.get("average_speed_kmph", record.get("average_speed", 0))),
                    travel_time_delay_minutes=float(record.get("travel_time_delay_minutes", record.get("travel_time_delay", 0))),
                    incident_count=int(record.get("incident_count", 0)),
                    road_closure_count=int(record.get("road_closure_count", 0)),
                    latitude=float(record.get("latitude", 0)),
                    longitude=float(record.get("longitude", 0)),
                    raw_observation_id=raw.id,
                )
            )
        elif provider_type == "news":
            db.add(
                NewsObservation(
                    provider_name=provider_name,
                    district_id=raw.district_id,
                    published_at=raw.observed_at,
                    title=str(record.get("title", "")),
                    summary=str(record.get("summary", "")),
                    url=str(record.get("url", "")),
                    source_name=str(record.get("source", "")),
                    category=str(record.get("category", "")),
                    severity=str(record.get("severity", "")),
                    inferred_latitude=float(record.get("latitude", 0)),
                    inferred_longitude=float(record.get("longitude", 0)),
                    raw_observation_id=raw.id,
                )
            )
        elif provider_type == "aqi":
            db.add(
                AQIObservation(
                    provider_name=provider_name,
                    district_id=raw.district_id,
                    observed_at=raw.observed_at,
                    aqi=float(record.get("aqi", 0)),
                    pm25=float(record.get("pm25", 0)),
                    pm10=float(record.get("pm10", 0)),
                    category=str(record.get("category", "")),
                    health_advisory=str(record.get("health_advisory", "")),
                    raw_observation_id=raw.id,
                )
            )
        count += 1
    db.commit()
    return count


def list_observations(
    db: Session,
    observation_type: str,
    district_id: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    model_map = {
        "weather": WeatherObservation,
        "traffic": TrafficObservation,
        "news": NewsObservation,
        "aqi": AQIObservation,
    }
    model = model_map.get(observation_type)
    if not model:
        return []
    query = db.query(model)
    if district_id:
        query = query.filter(model.district_id == district_id)
    rows = query.order_by(model.id.desc()).limit(limit).all()
    return [_serialize(row) for row in rows]


def cleanup_old_observations(db: Session) -> int:
    cutoff = datetime.utcnow() - timedelta(days=get_settings().provider_observation_retention_days)
    deleted = db.query(ProviderObservation).filter(ProviderObservation.created_at < cutoff).delete()
    for model in [WeatherObservation, TrafficObservation, NewsObservation, AQIObservation]:
        date_column = getattr(model, "observed_at", getattr(model, "published_at", None))
        if date_column is not None:
            db.query(model).filter(date_column < cutoff).delete()
    db.commit()
    return int(deleted)


def _serialize(row: Any) -> dict[str, Any]:
    result = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        result[column.name] = value.isoformat() if isinstance(value, datetime) else value
    return result


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            return datetime.utcnow()
    return datetime.utcnow()
