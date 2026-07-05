from __future__ import annotations

import csv
import io
import json
import math
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any, Protocol

from app.config import get_settings
from app.services.data_loader import load_all_data


KEYWORDS = [
    "flood",
    "waterlogging",
    "heatwave",
    "AQI",
    "pollution",
    "fire",
    "earthquake",
    "industrial accident",
    "traffic jam",
    "road closure",
    "power outage",
    "water shortage",
    "hospital overload",
    "civic complaint",
]


class NewsProvider(Protocol):
    def fetch(self) -> list[dict[str, Any]]:
        ...


class WeatherProvider(Protocol):
    def fetch(self) -> list[dict[str, Any]]:
        ...


class TrafficProvider(Protocol):
    def fetch(self) -> list[dict[str, Any]]:
        ...


class GDELTNewsProvider:
    def fetch(self) -> list[dict[str, Any]]:
        query = urllib.parse.quote(
            "(Delhi OR Gurugram OR Noida OR Ghaziabad OR Faridabad OR Meerut OR NCR) "
            "(flood OR waterlogging OR heatwave OR AQI OR pollution OR fire OR traffic OR outage)"
        )
        url = (
            "https://api.gdeltproject.org/api/v2/doc/doc"
            f"?query={query}&mode=ArtList&format=json&maxrecords=20&sort=HybridRel"
        )
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        items = []
        for article in payload.get("articles", []):
            title = article.get("title", "NCR civic signal")
            district = infer_district(f"{title} {article.get('seendate', '')}")
            category = infer_category(title)
            items.append(
                {
                    "title": title,
                    "source": article.get("sourceCountry", "GDELT"),
                    "url": article.get("url", ""),
                    "published_at": article.get("seendate", datetime.utcnow().isoformat()),
                    "district_id": district["ward_id"],
                    "district_name": district["ward_name"],
                    "category": category,
                    "severity": infer_severity(category),
                    "summary": article.get("domain", "News-derived NCR civic signal"),
                    "latitude": district["latitude"],
                    "longitude": district["longitude"],
                }
            )
        return items


class NewsApiProvider:
    def fetch(self) -> list[dict[str, Any]]:
        api_key = get_settings().news_api_key
        if not api_key:
            return []
        query = urllib.parse.quote("Delhi NCR flood OR heatwave OR AQI OR traffic OR fire")
        url = f"https://newsapi.org/v2/everything?q={query}&language=en&pageSize=20&apiKey={api_key}"
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []
        items = []
        for article in payload.get("articles", []):
            title = article.get("title") or "NCR civic news"
            district = infer_district(title)
            category = infer_category(title)
            items.append(
                {
                    "title": title,
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                    "district_id": district["ward_id"],
                    "district_name": district["ward_name"],
                    "category": category,
                    "severity": infer_severity(category),
                    "summary": article.get("description") or title,
                    "latitude": district["latitude"],
                    "longitude": district["longitude"],
                }
            )
        return items


class OpenWeatherProvider:
    def fetch(self) -> list[dict[str, Any]]:
        api_key = get_settings().openweather_api_key
        if not api_key:
            return fallback_weather()
        observations = []
        for district in district_records():
            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?lat={district['latitude']}&lon={district['longitude']}&units=metric&appid={api_key}"
            )
            try:
                with urllib.request.urlopen(url, timeout=8) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception:
                continue
            main = payload.get("main", {})
            wind = payload.get("wind", {})
            rainfall = payload.get("rain", {}).get("1h", 0)
            observations.append(
                {
                    "district_id": district["ward_id"],
                    "district_name": district["ward_name"],
                    "temperature": main.get("temp", 0),
                    "feels_like": main.get("feels_like", 0),
                    "humidity": main.get("humidity", 0),
                    "rainfall": rainfall,
                    "wind_speed": wind.get("speed", 0),
                    "weather_condition": payload.get("weather", [{}])[0].get("main", "Unknown"),
                    "heat_index": calculate_heat_index(main.get("temp", 0), main.get("humidity", 0)),
                    "forecast": fallback_forecast(main.get("temp", 35), rainfall),
                    "latitude": district["latitude"],
                    "longitude": district["longitude"],
                }
            )
        return observations or fallback_weather()


class IMDProvider:
    """IMD-compatible provider for configurable JSON, CSV, or RSS/XML feeds."""

    def fetch(self) -> list[dict[str, Any]]:
        settings = get_settings()
        if not settings.imd_feed_url:
            return []
        headers = {"User-Agent": "CivicIQ/1.0"}
        if settings.imd_api_key:
            headers["Authorization"] = f"Bearer {settings.imd_api_key}"
        try:
            request = urllib.request.Request(settings.imd_feed_url, headers=headers)
            with urllib.request.urlopen(request, timeout=8) as response:
                content = response.read().decode("utf-8")
                content_type = response.headers.get("content-type", "")
        except Exception:
            return []
        if "json" in content_type or content.strip().startswith(("{", "[")):
            return _parse_imd_json(content)
        if "csv" in content_type or "," in content.splitlines()[0]:
            return _parse_imd_csv(content)
        return _parse_imd_xml(content)


class TomTomTrafficProvider:
    def fetch(self) -> list[dict[str, Any]]:
        api_key = get_settings().tomtom_api_key
        if not api_key:
            return []
        observations = []
        for district in district_records():
            url = (
                "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
                f"?point={district['latitude']},{district['longitude']}&key={api_key}"
            )
            try:
                with urllib.request.urlopen(url, timeout=8) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception:
                continue
            flow = payload.get("flowSegmentData", {})
            observations.append(
                normalize_traffic_record(
                    provider_name="TomTom",
                    district=district,
                    current_speed=flow.get("currentSpeed", 0),
                    free_flow_speed=flow.get("freeFlowSpeed", 1),
                    route_name=route_for_district(district["ward_name"]),
                    incidents=0,
                    closures=0,
                )
            )
        return observations


class MapboxTrafficProvider:
    def fetch(self) -> list[dict[str, Any]]:
        token = get_settings().mapbox_access_token
        if not token:
            return []
        observations = []
        for district in district_records():
            # Mapbox does not expose a simple free traffic metric endpoint for all plans.
            # This adapter validates token-reachable map matching/directions style access
            # and normalizes a conservative estimate from representative route distance.
            lon = district["longitude"]
            lat = district["latitude"]
            url = (
                "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"
                f"{lon},{lat};{lon + 0.08},{lat + 0.04}?access_token={token}&overview=false"
            )
            try:
                with urllib.request.urlopen(url, timeout=8) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                route = payload.get("routes", [{}])[0]
            except Exception:
                continue
            duration = float(route.get("duration", 0)) / 60
            distance_km = float(route.get("distance", 1)) / 1000
            speed = distance_km / max(duration / 60, 0.01)
            observations.append(
                normalize_traffic_record(
                    provider_name="Mapbox",
                    district=district,
                    current_speed=speed,
                    free_flow_speed=max(speed * 1.35, 1),
                    route_name=route_for_district(district["ward_name"]),
                    incidents=0,
                    closures=0,
                )
            )
        return observations


class GoogleMapsTrafficProvider:
    def fetch(self) -> list[dict[str, Any]]:
        api_key = get_settings().google_maps_api_key
        if not api_key:
            return []
        observations = []
        for district in district_records():
            origin = f"{district['latitude']},{district['longitude']}"
            destination = f"{district['latitude'] + 0.05},{district['longitude'] + 0.08}"
            url = (
                "https://maps.googleapis.com/maps/api/distancematrix/json"
                f"?origins={origin}&destinations={destination}&departure_time=now&key={api_key}"
            )
            try:
                with urllib.request.urlopen(url, timeout=8) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                element = payload.get("rows", [{}])[0].get("elements", [{}])[0]
            except Exception:
                continue
            duration = element.get("duration", {}).get("value", 1)
            traffic_duration = element.get("duration_in_traffic", {}).get("value", duration)
            congestion = min(100, max(0, (traffic_duration - duration) / max(duration, 1) * 100))
            observations.append(
                {
                    "provider_name": "GoogleMaps",
                    "district_id": district["ward_id"],
                    "district_name": district["ward_name"],
                    "congestion_level": round(congestion, 1),
                    "average_speed": round(35 * (1 - congestion / 140), 1),
                    "incident_count": 0,
                    "road_closure_count": 0,
                    "travel_time_delay": round((traffic_duration - duration) / 60, 1),
                    "affected_route_name": route_for_district(district["ward_name"]),
                    "latitude": district["latitude"],
                    "longitude": district["longitude"],
                }
            )
        return observations


class FallbackTrafficProvider:
    def fetch(self) -> list[dict[str, Any]]:
        observations = []
        for index, district in enumerate(district_records()):
            congestion = min(100, 42 + index * 4 + (18 if district["ward_id"] in {"NCR01", "NCR04", "NCR05"} else 0))
            observations.append(
                {
                    "district_id": district["ward_id"],
                    "district_name": district["ward_name"],
                    "congestion_level": congestion,
                    "average_speed": max(8, 44 - congestion * 0.28),
                    "incident_count": 1 + index % 5,
                    "road_closure_count": 1 if congestion > 75 else 0,
                    "travel_time_delay": round(congestion * 0.42, 1),
                    "affected_route_name": route_for_district(district["ward_name"]),
                    "latitude": district["latitude"],
                    "longitude": district["longitude"],
                }
            )
        return observations


class BhuvanProvider:
    """Bhuvan-compatible abstraction for future official geospatial integration."""

    def fetch_layers(self) -> list[dict[str, Any]]:
        return []


def fetch_news_items() -> list[dict[str, Any]]:
    settings = get_settings()
    providers: list[NewsProvider] = []
    if settings.news_api_key:
        providers.append(NewsApiProvider())
    providers.append(GDELTNewsProvider())

    for provider in providers:
        items = provider.fetch()
        if items:
            return items
    return fallback_news()


def fetch_weather_observations() -> list[dict[str, Any]]:
    imd_records = IMDProvider().fetch()
    if imd_records:
        return imd_records
    return OpenWeatherProvider().fetch()


def fetch_traffic_observations() -> list[dict[str, Any]]:
    for provider in [TomTomTrafficProvider(), MapboxTrafficProvider(), GoogleMapsTrafficProvider()]:
        records = provider.fetch()
        if records:
            return records
    return FallbackTrafficProvider().fetch()


def fetch_environmental_observations() -> list[dict[str, Any]]:
    data = load_all_data()
    latest = data["air_quality"].groupby("ward_id", as_index=False).tail(1)
    districts = {record["ward_id"]: record for record in district_records()}
    return [
        {
            "district_id": row["ward_id"],
            "district_name": districts[row["ward_id"]]["ward_name"],
            "aqi": int(row["aqi"]),
            "pm25": float(row["pm25"]),
            "pm10": round(float(row["pm25"]) * 1.8, 1),
            "category": "AQI/Public Health",
            "severity": "Critical" if row["aqi"] >= 250 else "High" if row["aqi"] >= 150 else "Medium",
            "latitude": districts[row["ward_id"]]["latitude"],
            "longitude": districts[row["ward_id"]]["longitude"],
        }
        for _, row in latest.iterrows()
    ]


def fallback_weather() -> list[dict[str, Any]]:
    observations = []
    for index, district in enumerate(district_records()):
        temp = 38 + (index % 5) * 1.7
        humidity = 42 + (index % 4) * 7
        rainfall = 32 if "flood" in district["disaster_profile"].lower() else index % 6
        observations.append(
            {
                "district_id": district["ward_id"],
                "district_name": district["ward_name"],
                "temperature": round(temp, 1),
                "feels_like": round(temp + humidity * 0.05, 1),
                "humidity": humidity,
                "rainfall": rainfall,
                "wind_speed": round(8 + index * 0.4, 1),
                "weather_condition": "Monsoon risk" if rainfall >= 25 else "Hot and humid",
                "heat_index": calculate_heat_index(temp, humidity),
                "forecast": fallback_forecast(temp, rainfall),
                "latitude": district["latitude"],
                "longitude": district["longitude"],
            }
        )
    return observations


def normalize_traffic_record(
    provider_name: str,
    district: dict[str, Any],
    current_speed: float,
    free_flow_speed: float,
    route_name: str,
    incidents: int,
    closures: int,
) -> dict[str, Any]:
    congestion = max(0, min(100, (1 - (float(current_speed) / max(float(free_flow_speed), 1))) * 100))
    delay = max(0, congestion * 0.35)
    return {
        "provider_name": provider_name,
        "district_id": district["ward_id"],
        "district_name": district["ward_name"],
        "congestion_level": round(congestion, 1),
        "average_speed": round(float(current_speed), 1),
        "incident_count": int(incidents),
        "road_closure_count": int(closures),
        "travel_time_delay": round(delay, 1),
        "affected_route_name": route_name,
        "latitude": district["latitude"],
        "longitude": district["longitude"],
    }


def _parse_imd_json(content: str) -> list[dict[str, Any]]:
    payload = json.loads(content)
    records = payload if isinstance(payload, list) else payload.get("alerts") or payload.get("records") or []
    return [_normalize_imd_record(record) for record in records if _normalize_imd_record(record)]


def _parse_imd_csv(content: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(content))
    return [_normalize_imd_record(row) for row in reader if _normalize_imd_record(row)]


def _parse_imd_xml(content: str) -> list[dict[str, Any]]:
    root = ET.fromstring(content)
    records = []
    for item in root.findall(".//item"):
        title = item.findtext("title", default="")
        description = item.findtext("description", default="")
        records.append(_normalize_imd_record({"title": title, "description": description, "district": title}))
    return [record for record in records if record]


def _normalize_imd_record(record: dict[str, Any]) -> dict[str, Any] | None:
    text = " ".join(str(record.get(key, "")) for key in ["district", "title", "description", "alert_type"])
    if not text.strip():
        return None
    district = infer_district(text)
    alert_type = infer_category(text)
    temperature = float(record.get("temperature") or record.get("temp") or 38)
    humidity = float(record.get("humidity") or 50)
    rainfall = float(record.get("rainfall") or record.get("rainfall_mm") or 0)
    return {
        "provider_name": "IMD",
        "district_id": district["ward_id"],
        "district_name": district["ward_name"],
        "temperature": temperature,
        "feels_like": float(record.get("feels_like") or calculate_heat_index(temperature, humidity)),
        "humidity": humidity,
        "rainfall": rainfall,
        "wind_speed": float(record.get("wind_speed") or 0),
        "weather_condition": str(record.get("condition") or alert_type),
        "heat_index": calculate_heat_index(temperature, humidity),
        "forecast": fallback_forecast(temperature, rainfall),
        "alert_type": alert_type,
        "severity": infer_severity(alert_type),
        "description": str(record.get("description") or record.get("title") or alert_type),
        "latitude": district["latitude"],
        "longitude": district["longitude"],
    }


def fallback_news() -> list[dict[str, Any]]:
    items = []
    templates = [
        ("Yamuna floodplain waterlogging watch issued", "Flood", "NCR01"),
        ("AQI and respiratory health concerns rise in Ghaziabad", "AQI/Public Health", "NCR04"),
        ("Heatwave response teams prepare cooling shelters in Alwar", "Heatwave", "NCR15"),
        ("Traffic jam reported on Noida-Greater Noida expressway", "Traffic", "NCR05"),
        ("Industrial fire drill escalated in Panipat belt", "Fire/Industrial", "NCR08"),
    ]
    districts = {record["ward_id"]: record for record in district_records()}
    for title, category, district_id in templates:
        district = districts[district_id]
        items.append(
            {
                "title": title,
                "source": "Fallback NCR Monitor",
                "url": "",
                "published_at": datetime.utcnow().isoformat(),
                "district_id": district_id,
                "district_name": district["ward_name"],
                "category": category,
                "severity": infer_severity(category),
                "summary": title,
                "latitude": district["latitude"],
                "longitude": district["longitude"],
            }
        )
    return items


def district_records() -> list[dict[str, Any]]:
    return load_all_data()["wards"].to_dict(orient="records")


def infer_district(text: str) -> dict[str, Any]:
    normalized = text.lower()
    for district in district_records():
        aliases = [district["ward_name"].lower(), district["ward_name"].split("/")[0].lower()]
        if any(alias.split()[0] in normalized for alias in aliases):
            return district
    if "noida" in normalized:
        return next(item for item in district_records() if item["ward_id"] == "NCR05")
    if "delhi" in normalized:
        return next(item for item in district_records() if item["ward_id"] == "NCR01")
    return district_records()[0]


def infer_category(text: str) -> str:
    normalized = text.lower()
    if any(term in normalized for term in ["flood", "waterlogging", "rain"]):
        return "Flood"
    if "heat" in normalized:
        return "Heatwave"
    if any(term in normalized for term in ["aqi", "pollution", "air"]):
        return "AQI/Public Health"
    if any(term in normalized for term in ["traffic", "road closure", "jam"]):
        return "Traffic"
    if any(term in normalized for term in ["fire", "industrial"]):
        return "Fire/Industrial"
    if any(term in normalized for term in ["power", "water shortage", "outage"]):
        return "Utility"
    if "earthquake" in normalized:
        return "Seismic"
    return "News-Derived Incident"


def infer_severity(category: str) -> str:
    return {
        "Flood": "High",
        "Heatwave": "High",
        "AQI/Public Health": "High",
        "Fire/Industrial": "High",
        "Seismic": "Critical",
        "Traffic": "Medium",
        "Utility": "Medium",
    }.get(category, "Medium")


def calculate_heat_index(temperature_c: float, humidity: float) -> float:
    return round(temperature_c + 0.05 * humidity + max(0, temperature_c - 35) * 0.4, 1)


def fallback_forecast(base_temperature: float, base_rainfall: float) -> list[dict[str, Any]]:
    today = datetime.utcnow().date()
    return [
        {
            "date": (today + timedelta(days=offset)).isoformat(),
            "max_temperature": round(base_temperature + offset * 0.6, 1),
            "rainfall": round(max(0, base_rainfall - offset * 2), 1),
        }
        for offset in range(1, 6)
    ]


def route_for_district(name: str) -> str:
    if "Delhi" in name:
        return "Ring Road / NH-48"
    if "Ghaziabad" in name:
        return "NH-9 / Hindon corridor"
    if "Noida" in name:
        return "Noida-Greater Noida Expressway"
    if "Gurugram" in name:
        return "NH-48 Cyber City corridor"
    return "NCR arterial corridor"
