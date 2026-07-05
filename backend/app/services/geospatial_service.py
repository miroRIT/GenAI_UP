from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.services.data_loader import load_all_data
from app.services.provider_service import (
    fetch_environmental_observations,
    fetch_news_items,
    fetch_traffic_observations,
    fetch_weather_observations,
)


def ensure_geojson() -> None:
    geojson_dir = get_settings().geojson_dir
    geojson_dir.mkdir(parents=True, exist_ok=True)
    path = geojson_dir / "ncr_districts.geojson"
    if path.exists():
        return
    path.write_text(json.dumps(build_district_geojson(), indent=2), encoding="utf-8")


def build_district_geojson() -> dict[str, Any]:
    data = load_all_data()
    features = []
    for _, district in data["wards"].iterrows():
        lat = float(district["latitude"])
        lon = float(district["longitude"])
        area_factor = max(0.12, min(0.38, float(district["area_sq_km"]) / 30000))
        polygon = [
            [lon - area_factor, lat - area_factor],
            [lon + area_factor, lat - area_factor * 0.72],
            [lon + area_factor * 0.78, lat + area_factor],
            [lon - area_factor * 0.8, lat + area_factor * 0.82],
            [lon - area_factor, lat - area_factor],
        ]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "district_id": district["ward_id"],
                    "district_name": district["ward_name"],
                    "state": district["state"],
                    "population": int(district["population"]),
                    "area_sq_km": int(district["area_sq_km"]),
                    "disaster_profile": district["disaster_profile"],
                    "note": "Simplified demo polygon. Production should use official NCR/Bhuvan/Survey of India/state GIS boundaries.",
                },
                "geometry": {"type": "Polygon", "coordinates": [polygon]},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def get_district_geojson() -> dict[str, Any]:
    ensure_geojson()
    path = get_settings().geojson_dir / "ncr_districts.geojson"
    return json.loads(path.read_text(encoding="utf-8"))


def get_available_layers() -> list[dict[str, Any]]:
    return [
        {"id": "districts", "name": "District boundaries", "source": "Local simplified GeoJSON"},
        {"id": "weather", "name": "Weather", "source": "OpenWeather or fallback"},
        {"id": "traffic", "name": "Traffic", "source": "Google/TomTom/Mapbox abstraction or fallback"},
        {"id": "aqi", "name": "AQI", "source": "Sample CPCB-like readings"},
        {"id": "flood", "name": "Flood risk", "source": "Risk engine + news/weather"},
        {"id": "heatwave", "name": "Heatwave risk", "source": "Weather + vulnerability"},
        {"id": "fire", "name": "Fire/industrial risk", "source": "Incidents + industrial proxy"},
        {"id": "news", "name": "News incidents", "source": "GDELT/NewsAPI/fallback"},
        {"id": "alerts", "name": "Operational alerts", "source": "CivicIQ alert workflow"},
    ]


def get_mapped_incidents() -> list[dict[str, Any]]:
    incidents = []
    for item in fetch_news_items():
        incidents.append(
            {
                "incident_id": f"news-{abs(hash(item['title']))}",
                "title": item["title"],
                "district_id": item["district_id"],
                "district_name": item["district_name"],
                "category": item["category"],
                "severity": item["severity"],
                "timestamp": item["published_at"],
                "source": item["source"],
                "url": item["url"],
                "summary": item["summary"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "recommended_action": recommended_action_for_category(item["category"]),
            }
        )
    for item in fetch_weather_observations():
        if item["heat_index"] >= 43 or item["rainfall"] >= 25:
            category = "Heatwave" if item["heat_index"] >= 43 else "Flood"
            incidents.append(
                {
                    "incident_id": f"weather-{item['district_id']}",
                    "title": f"{category} watch: {item['district_name']}",
                    "district_id": item["district_id"],
                    "district_name": item["district_name"],
                    "category": category,
                    "severity": "High",
                    "timestamp": item.get("observed_at", ""),
                    "source": "Weather Provider",
                    "url": "",
                    "summary": f"Heat index {item['heat_index']} C, rainfall {item['rainfall']} mm",
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "recommended_action": recommended_action_for_category(category),
                }
            )
    for item in fetch_traffic_observations():
        if item["congestion_level"] >= 75:
            incidents.append(
                {
                    "incident_id": f"traffic-{item['district_id']}",
                    "title": f"Traffic congestion on {item['affected_route_name']}",
                    "district_id": item["district_id"],
                    "district_name": item["district_name"],
                    "category": "Traffic",
                    "severity": "High",
                    "timestamp": "",
                    "source": "Traffic Provider",
                    "url": "",
                    "summary": f"{item['congestion_level']}% congestion and {item['travel_time_delay']} min delay",
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "recommended_action": recommended_action_for_category("Traffic"),
                }
            )
    for item in fetch_environmental_observations():
        if item["aqi"] >= 150:
            incidents.append(
                {
                    "incident_id": f"aqi-{item['district_id']}",
                    "title": f"AQI public health advisory: {item['district_name']}",
                    "district_id": item["district_id"],
                    "district_name": item["district_name"],
                    "category": "AQI/Public Health",
                    "severity": item["severity"],
                    "timestamp": "",
                    "source": "Environmental Provider",
                    "url": "",
                    "summary": f"AQI {item['aqi']}, PM2.5 {item['pm25']}",
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "recommended_action": recommended_action_for_category("AQI/Public Health"),
                }
            )
    return incidents


def recommended_action_for_category(category: str) -> str:
    return {
        "Flood": "Activate drainage crews, inspect low-lying corridors, and prepare shelter routing.",
        "Heatwave": "Open cooling shelters, issue heat advisory, and prioritize vulnerable residents.",
        "AQI/Public Health": "Issue public health advisory and coordinate Pollution Control Board actions.",
        "Traffic": "Coordinate traffic police diversions and emergency route priority.",
        "Fire/Industrial": "Dispatch fire inspection team and isolate hazardous facility perimeter.",
        "Utility": "Coordinate utility repair crew and publish restoration timeline.",
    }.get(category, "Validate signal with district control room and assign responsible department.")
