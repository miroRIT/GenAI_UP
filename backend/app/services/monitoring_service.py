from __future__ import annotations

from datetime import datetime
from random import Random
from typing import Any

from app.services.data_loader import load_all_data
from app.services.risk_engine import calculate_ward_risk_scores


def get_region_profile() -> dict[str, Any]:
    data = load_all_data()
    wards = data["wards"]
    return {
        "region_name": "National Capital Region, India",
        "population": int(wards["population"].sum()),
        "population_label": "7.5 crore+",
        "area_sq_km": int(wards["area_sq_km"].sum()),
        "planning_note": "NCR spans Delhi plus districts in Haryana, Uttar Pradesh, and Rajasthan.",
        "states": sorted(wards["state"].unique().tolist()),
        "zone_count": int(len(wards)),
    }


def get_disaster_map_layers() -> dict[str, Any]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    layers = []

    for _, ward in scores.iterrows():
        disaster_score = _disaster_score(ward)
        layers.append(
            {
                "ward_id": ward["ward_id"],
                "ward_name": ward["ward_name"],
                "state": ward["state"],
                "latitude": ward["latitude"],
                "longitude": ward["longitude"],
                "population": int(ward["population"]),
                "area_sq_km": int(ward["area_sq_km"]),
                "community_risk_score": float(ward["community_risk_score"]),
                "risk_level": ward["risk_level"],
                "disaster_score": disaster_score,
                "primary_hazards": _primary_hazards(str(ward["disaster_profile"])),
                "disaster_profile": ward["disaster_profile"],
            }
        )

    return {
        "region": get_region_profile(),
        "bbox": {
            "north": float(scores["latitude"].max()),
            "south": float(scores["latitude"].min()),
            "east": float(scores["longitude"].max()),
            "west": float(scores["longitude"].min()),
        },
        "layers": sorted(layers, key=lambda item: item["disaster_score"], reverse=True),
    }


def get_live_monitoring_feed() -> dict[str, Any]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    randomizer = Random(datetime.now().strftime("%Y%m%d%H%M"))
    top_zones = scores.head(6)

    weather_alerts = []
    traffic_alerts = []
    news_alerts = []
    geospatial_alerts = []

    for _, zone in top_zones.iterrows():
        heat_index = round(randomizer.uniform(39.0, 47.5), 1)
        rainfall_mm = round(randomizer.uniform(0, 42), 1)
        congestion = int(min(100, randomizer.gauss(72, 14)))
        river_watch = "Yamuna/Hindon watch" if "flood" in str(zone["disaster_profile"]).lower() else "local drainage watch"

        weather_alerts.append(
            {
                "zone": zone["ward_name"],
                "signal": "Heat and rainfall nowcast",
                "value": f"Heat index {heat_index} C, rainfall {rainfall_mm} mm",
                "severity": "High" if heat_index >= 44 or rainfall_mm >= 30 else "Medium",
                "action": "Prepare cooling shelters and clear stormwater choke points.",
            }
        )
        traffic_alerts.append(
            {
                "zone": zone["ward_name"],
                "signal": "Corridor congestion",
                "value": f"{congestion}% congestion",
                "severity": "High" if congestion >= 78 else "Medium",
                "action": "Coordinate traffic police diversions and emergency route priority.",
            }
        )
        news_alerts.append(
            {
                "zone": zone["ward_name"],
                "signal": "Civic news monitor",
                "value": _news_signal(zone["ward_name"], str(zone["disaster_profile"])),
                "severity": zone["risk_level"],
                "action": "Validate with district control room and publish public advisory if confirmed.",
            }
        )
        geospatial_alerts.append(
            {
                "zone": zone["ward_name"],
                "signal": river_watch,
                "value": f"Disaster score {round(_disaster_score(zone), 1)}",
                "severity": zone["risk_level"],
                "action": "Overlay shelters, hospitals, drains, floodplains, and incident hotspots.",
            }
        )

    return {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "mock-live feed; provider adapters can be attached with API keys",
        "providers_ready": [
            "NewsAPI/GDELT for news",
            "IMD/OpenWeather for weather",
            "Mapbox/Google Maps/TomTom for traffic",
            "Bhuvan/OSM/GeoJSON layers for geospatial data",
        ],
        "weather": weather_alerts,
        "traffic": traffic_alerts,
        "news": news_alerts,
        "geospatial": geospatial_alerts,
    }


def _primary_hazards(disaster_profile: str) -> list[str]:
    hazard_terms = ["flood", "heat", "AQI", "seismic", "drought", "fire", "traffic", "water stress"]
    normalized_profile = disaster_profile.lower()
    hazards = [term for term in hazard_terms if term.lower() in normalized_profile]
    return hazards or ["multi-hazard civic risk"]


def _disaster_score(ward: Any) -> float:
    profile = str(ward["disaster_profile"]).lower()
    hazard_count = sum(term in profile for term in ["flood", "heat", "aqi", "seismic", "drought", "fire", "water stress"])
    vulnerable = float(ward["vulnerable_population_percentage"])
    risk = float(ward["community_risk_score"])
    return round(min(100, risk * 0.55 + vulnerable * 0.9 + hazard_count * 7), 1)


def _news_signal(zone_name: str, disaster_profile: str) -> str:
    if "AQI" in disaster_profile or "air" in disaster_profile:
        return f"Air quality complaints and GRAP readiness mentions rising around {zone_name}."
    if "flood" in disaster_profile:
        return f"Drainage, waterlogging, and floodplain monitoring mentions rising around {zone_name}."
    if "heat" in disaster_profile:
        return f"Heat stress and water availability mentions rising around {zone_name}."
    return f"Local service disruption mentions rising around {zone_name}."
