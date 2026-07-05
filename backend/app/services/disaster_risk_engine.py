from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.data_loader import load_all_data
from app.services.provider_service import (
    fetch_environmental_observations,
    fetch_news_items,
    fetch_traffic_observations,
    fetch_weather_observations,
)
from app.services.risk_engine import classify_risk


DISASTER_WEIGHTS = {
    "flood": 0.20,
    "heatwave": 0.20,
    "aqi_public_health": 0.20,
    "industrial_fire": 0.15,
    "drought_water_stress": 0.15,
    "seismic": 0.10,
}


def calculate_disaster_risk() -> list[dict[str, Any]]:
    data = load_all_data()
    districts = data["wards"].copy()
    weather = _index(fetch_weather_observations())
    traffic = _index(fetch_traffic_observations())
    environment = _index(fetch_environmental_observations())
    news = fetch_news_items()
    news_by_district: dict[str, list[dict[str, Any]]] = {}
    for item in news:
        news_by_district.setdefault(item["district_id"], []).append(item)

    results = []
    for _, district in districts.iterrows():
        district_id = district["ward_id"]
        result = calculate_disaster_risk_for_district(
            district.to_dict(),
            weather.get(district_id, {}),
            traffic.get(district_id, {}),
            environment.get(district_id, {}),
            news_by_district.get(district_id, []),
            data,
        )
        results.append(result)
    return sorted(results, key=lambda item: item["overall"]["score"], reverse=True)


def get_disaster_risk_for_district(district_id: str) -> dict[str, Any] | None:
    for item in calculate_disaster_risk():
        if item["district_id"] == district_id:
            return item
    return None


def get_disaster_risk_type(district_id: str, risk_type: str) -> dict[str, Any] | None:
    district = get_disaster_risk_for_district(district_id)
    if not district:
        return None
    return district["risks"].get(risk_type)


def calculate_disaster_risk_for_district(
    district: dict[str, Any],
    weather: dict[str, Any],
    traffic: dict[str, Any],
    environment: dict[str, Any],
    news_items: list[dict[str, Any]],
    data: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    district_id = district["ward_id"]
    profile = str(district["disaster_profile"]).lower()
    vulnerable = float(district["vulnerable_population_percentage"])
    density = float(district["population"]) / max(1, float(district["area_sq_km"]))
    complaints = data["citizen_complaints"]
    ward_complaints = complaints[complaints["ward_id"] == district_id]
    utility_count = len(data["utility_outages"][data["utility_outages"]["ward_id"] == district_id])
    fire_count = len(
        data["emergency_incidents"][
            (data["emergency_incidents"]["ward_id"] == district_id)
            & (data["emergency_incidents"]["incident_type"].str.contains("fire", case=False))
        ]
    )

    flood = _score(
        [
            weather.get("rainfall", 0) * 2,
            _contains(profile, "flood") * 35,
            _contains(profile, "yamuna") * 20,
            _news_count(news_items, ["flood", "waterlogging"]) * 12,
            _complaint_category_count(ward_complaints, ["water", "roads"]) * 0.08,
        ],
        ["recent/forecast rainfall", "floodplain proximity", "river/canal exposure", "news alerts", "drainage complaints"],
        "Flood risk combines rainfall, low-lying/floodplain indicators, drainage complaints, and flood-related news.",
    )
    heatwave = _score(
        [
            max(0, weather.get("feels_like", 38) - 35) * 8,
            max(0, weather.get("heat_index", 40) - 38) * 7,
            vulnerable * 1.2,
            min(100, density / 350),
            _contains(profile, "heat") * 25,
        ],
        ["feels-like temperature", "heat index", "vulnerable population", "urban density", "heat exposure profile"],
        "Heatwave risk uses current heat stress, vulnerability, density, and district heat exposure.",
    )
    aqi = _score(
        [
            environment.get("aqi", 80) * 0.45,
            environment.get("pm25", 30) * 0.5,
            _news_count(news_items, ["aqi", "pollution"]) * 15,
            _contains(profile, "aqi") * 30,
            vulnerable,
        ],
        ["AQI", "PM2.5", "pollution news", "known AQI profile", "vulnerable population"],
        "AQI/public health risk combines pollutant levels, pollution signals, healthcare exposure, and vulnerable population.",
    )
    seismic = _score(
        [
            55,
            min(35, density / 600),
            _contains(profile, "seismic") * 25,
            _news_count(news_items, ["earthquake"]) * 25,
            max(0, 80 - float(district["service_coverage_score"])) * 0.45,
        ],
        ["NCR seismic baseline", "population density", "seismic profile", "earthquake alerts", "infrastructure vulnerability proxy"],
        "Seismic exposure uses NCR baseline, density, infrastructure proxy, and earthquake-related alerts.",
    )
    drought = _score(
        [
            max(0, 20 - weather.get("rainfall", 0)) * 2,
            max(0, weather.get("temperature", 38) - 36) * 5,
            _news_count(news_items, ["water shortage", "drought"]) * 20,
            _contains(profile, "water stress") * 30 + _contains(profile, "drought") * 30,
            utility_count * 4,
        ],
        ["rainfall deficit", "temperature", "water-shortage news", "groundwater stress proxy", "utility issue count"],
        "Drought/water-stress risk combines low rainfall, heat, water-stress profile, and utility disruptions.",
    )
    industrial_fire = _score(
        [
            _contains(profile, "industrial") * 35,
            _contains(profile, "fire") * 25,
            fire_count * 12,
            max(0, weather.get("temperature", 38) - 36) * 4,
            _news_count(news_items, ["fire", "industrial accident"]) * 25,
        ],
        ["industrial area proxy", "fire profile", "fire incidents", "heat conditions", "industrial/fire news"],
        "Industrial/fire risk combines industrial presence, fire incidents, heat, and news-derived accident signals.",
    )

    risks = {
        "flood": flood,
        "heatwave": heatwave,
        "aqi_public_health": aqi,
        "seismic": seismic,
        "drought_water_stress": drought,
        "industrial_fire": industrial_fire,
    }
    overall_score = round(sum(risks[name]["score"] * weight for name, weight in DISASTER_WEIGHTS.items()), 1)
    return {
        "district_id": district_id,
        "district_name": district["ward_name"],
        "state": district["state"],
        "population": int(district["population"]),
        "area_sq_km": int(district["area_sq_km"]),
        "latitude": district["latitude"],
        "longitude": district["longitude"],
        "overall": {
            "score": overall_score,
            "level": classify_risk(overall_score),
            "explanation": "Weighted combined disaster risk across flood, heatwave, AQI/public health, industrial/fire, drought/water-stress, and seismic exposure.",
            "confidence": "Medium" if news_items else "Low-Medium",
            "data_sources_used": ["sample civic data", "weather provider/fallback", "environmental observations", "news provider/fallback"],
        },
        "risks": risks,
    }


def _score(values: list[float], factors: list[str], explanation: str) -> dict[str, Any]:
    score = round(max(0, min(100, sum(values) / max(1, len(values)) * 1.45)), 1)
    top_factors = [factor for _, factor in sorted(zip(values, factors), reverse=True)[:3]]
    return {
        "score": score,
        "level": classify_risk(score),
        "top_contributing_factors": top_factors,
        "explanation": explanation,
        "recommended_actions": _actions_for_factors(top_factors),
        "confidence": "Medium",
        "data_sources_used": ["provider/fallback feeds", "sample civic data", "district profile"],
    }


def _actions_for_factors(factors: list[str]) -> list[str]:
    actions = []
    joined = " ".join(factors).lower()
    if "rain" in joined or "flood" in joined or "drainage" in joined:
        actions.append("Pre-position pumps, clear drains, and verify shelter routes.")
    if "heat" in joined or "temperature" in joined:
        actions.append("Open cooling shelters and issue heat-health outreach.")
    if "aqi" in joined or "pollution" in joined:
        actions.append("Coordinate pollution-control checks and public health advisory.")
    if "fire" in joined or "industrial" in joined:
        actions.append("Inspect industrial clusters and stage fire response units.")
    if "water" in joined or "drought" in joined:
        actions.append("Monitor water supply, tankers, and groundwater-stress corridors.")
    if "seismic" in joined or "infrastructure" in joined:
        actions.append("Review critical infrastructure readiness and emergency communications.")
    return actions or ["Validate signal with district control room and monitor for escalation."]


def _index(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["district_id"]: record for record in records}


def _contains(text: str, term: str) -> int:
    return 1 if term in text else 0


def _news_count(items: list[dict[str, Any]], terms: list[str]) -> int:
    return sum(any(term in f"{item.get('title', '')} {item.get('summary', '')}".lower() for term in terms) for item in items)


def _complaint_category_count(complaints: pd.DataFrame, terms: list[str]) -> int:
    if complaints.empty:
        return 0
    return int(complaints["category"].str.lower().isin(terms).sum())
