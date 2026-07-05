from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
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
    """Placeholder for official IMD feed/API integration.

    Production wiring can map IMD station or grid feeds into the same weather
    observation schema used by OpenWeatherProvider.
    """

    def fetch(self) -> list[dict[str, Any]]:
        return []


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
    return OpenWeatherProvider().fetch()


def fetch_traffic_observations() -> list[dict[str, Any]]:
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
