from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import ProviderStatus
from app.services.geospatial_provider import list_boundary_sources, load_district_boundaries
from app.services.observation_service import persist_provider_records
from app.services.provider_service import (
    GDELTNewsProvider,
    NewsApiProvider,
    OpenWeatherProvider,
    fetch_environmental_observations,
    fetch_traffic_observations,
)


def provider_definitions() -> list[dict[str, Any]]:
    settings = get_settings()
    return [
        {"name": "NewsAPI", "type": "news", "configured": bool(settings.news_api_key), "env": "NEWS_API_KEY"},
        {"name": "GDELT", "type": "news", "configured": True, "env": None},
        {"name": "OpenWeather", "type": "weather", "configured": bool(settings.openweather_api_key), "env": "OPENWEATHER_API_KEY"},
        {"name": "IMD", "type": "weather", "configured": bool(settings.imd_feed_url or settings.imd_alert_feed_url), "env": "IMD_FEED_URL"},
        {"name": "TomTom", "type": "traffic", "configured": bool(settings.tomtom_api_key), "env": "TOMTOM_API_KEY"},
        {"name": "Mapbox", "type": "traffic", "configured": bool(settings.mapbox_access_token), "env": "MAPBOX_ACCESS_TOKEN"},
        {"name": "GoogleMaps", "type": "traffic", "configured": bool(settings.google_maps_api_key), "env": "GOOGLE_MAPS_API_KEY"},
        {"name": "FallbackTraffic", "type": "traffic", "configured": settings.mock_mode, "env": "MOCK_MODE"},
        {"name": "AQI Sample", "type": "aqi", "configured": True, "env": None},
        {"name": "BoundarySources", "type": "geospatial", "configured": True, "env": None},
    ]


def get_provider_status(db: Session) -> list[dict[str, Any]]:
    definitions = provider_definitions()
    stored = {status.provider_name: status for status in db.query(ProviderStatus).all()}
    result = []
    for definition in definitions:
        status = stored.get(definition["name"])
        result.append(
            {
                "provider_name": definition["name"],
                "provider_type": definition["type"],
                "configured": definition["configured"],
                "required_env": definition["env"],
                "last_success_at": status.last_success_at.isoformat() if status and status.last_success_at else None,
                "last_failure_at": status.last_failure_at.isoformat() if status and status.last_failure_at else None,
                "health_status": status.health_status if status else ("unknown" if definition["configured"] else "unavailable"),
                "last_error": status.last_error if status else (f"Missing {definition['env']}" if definition["env"] and not definition["configured"] else ""),
                "rate_limit_status": status.rate_limit_status if status else "unknown",
            }
        )
    return result


def test_provider(db: Session, provider_type: str) -> dict[str, Any]:
    tests: dict[str, tuple[str, Callable[[], list[dict[str, Any]]]]] = {
        "news": _news_test_callable(),
        "weather": ("OpenWeather" if get_settings().openweather_api_key else "OpenWeatherFallback", lambda: OpenWeatherProvider().fetch()[:3]),
        "traffic": ("TrafficProvider", lambda: fetch_traffic_observations()[:3]),
        "aqi": ("AQI Sample", lambda: fetch_environmental_observations()[:3]),
        "geospatial": ("BoundarySources", lambda: _geospatial_records(db)),
    }
    if provider_type not in tests:
        raise ValueError(f"Unsupported provider test: {provider_type}")
    provider_name, test_callable = tests[provider_type]
    configured = _is_configured(provider_name)
    if not configured and not get_settings().mock_mode and provider_name != "GDELT":
        return {
            "provider_name": provider_name,
            "provider_type": provider_type,
            "configured": False,
            "health_status": "unavailable",
            "message": "Provider key missing and MOCK_MODE=false.",
            "records": [],
        }
    try:
        records = test_callable()
        persist_provider_records(db, provider_name, provider_type, records)
        _upsert_status(db, provider_name, provider_type, configured, "healthy" if records else "degraded", "")
        return {
            "provider_name": provider_name,
            "provider_type": provider_type,
            "configured": configured,
            "health_status": "healthy" if records else "degraded",
            "records_processed": len(records),
            "sample": _sanitize_records(records[:2]),
        }
    except Exception as exc:
        _upsert_status(db, provider_name, provider_type, configured, "unavailable", str(exc))
        return {
            "provider_name": provider_name,
            "provider_type": provider_type,
            "configured": configured,
            "health_status": "unavailable",
            "last_error": str(exc),
            "records_processed": 0,
            "sample": [],
        }


def test_all_providers(db: Session) -> dict[str, Any]:
    return {provider_type: test_provider(db, provider_type) for provider_type in ["news", "weather", "traffic", "aqi", "geospatial"]}


def _news_test_callable() -> tuple[str, Callable[[], list[dict[str, Any]]]]:
    if get_settings().news_api_key:
        return "NewsAPI", lambda: NewsApiProvider().fetch()[:3]
    return "GDELT", lambda: GDELTNewsProvider().fetch()[:3]


def _is_configured(provider_name: str) -> bool:
    return next((definition["configured"] for definition in provider_definitions() if definition["name"] == provider_name), True)


def _upsert_status(
    db: Session,
    provider_name: str,
    provider_type: str,
    configured: bool,
    health_status: str,
    error: str,
) -> None:
    status = db.get(ProviderStatus, provider_name)
    now = datetime.utcnow()
    if not status:
        status = ProviderStatus(provider_name=provider_name, provider_type=provider_type)
        db.add(status)
    status.configured = 1 if configured else 0
    status.health_status = health_status
    status.last_error = error
    if error:
        status.last_failure_at = now
    else:
        status.last_success_at = now
    db.commit()


def _sanitize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized = []
    for record in records:
        sanitized.append({key: value for key, value in record.items() if "key" not in key.lower() and "token" not in key.lower()})
    return sanitized


def _geospatial_records(db: Session) -> list[dict[str, Any]]:
    geojson = load_district_boundaries(db, source="auto")
    return [
        {
            "district_id": feature["properties"].get("district_id", ""),
            "district_name": feature["properties"].get("district_name", ""),
            "source": geojson.get("metadata", {}).get("source_name", "Boundary source"),
            "is_official": geojson.get("metadata", {}).get("is_official", False),
        }
        for feature in geojson.get("features", [])[:3]
    ] or list_boundary_sources(db)[:3]
