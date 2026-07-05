"""Generate realistic mock urban telemetry for the dashboard and RAG agent.

The simulator intentionally models simple real-world relationships:
- traffic congestion rises during morning and evening rush hours
- emergency call volume slightly increases emergency response times
- air quality worsens when congestion is high
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from math import exp
from random import Random
from typing import Any


CITY_SECTORS = (
    "Central Business District",
    "North Residential Corridor",
    "East Industrial Zone",
    "South Medical District",
    "West Transit Hub",
    "Harbor Logistics Quarter",
)


SECTOR_PROFILES: dict[str, dict[str, float]] = {
    "Central Business District": {
        "traffic_baseline": 58,
        "aqi_baseline": 82,
        "emergency_baseline": 18,
        "response_baseline": 7.4,
    },
    "North Residential Corridor": {
        "traffic_baseline": 42,
        "aqi_baseline": 58,
        "emergency_baseline": 12,
        "response_baseline": 8.2,
    },
    "East Industrial Zone": {
        "traffic_baseline": 49,
        "aqi_baseline": 104,
        "emergency_baseline": 10,
        "response_baseline": 9.1,
    },
    "South Medical District": {
        "traffic_baseline": 46,
        "aqi_baseline": 66,
        "emergency_baseline": 22,
        "response_baseline": 6.5,
    },
    "West Transit Hub": {
        "traffic_baseline": 64,
        "aqi_baseline": 76,
        "emergency_baseline": 16,
        "response_baseline": 7.8,
    },
    "Harbor Logistics Quarter": {
        "traffic_baseline": 53,
        "aqi_baseline": 94,
        "emergency_baseline": 14,
        "response_baseline": 8.8,
    },
}


@dataclass(frozen=True)
class UrbanTelemetryRecord:
    """Single-sector telemetry snapshot used by dashboards and agent retrieval."""

    sector_id: str
    sector_name: str
    timestamp: str
    traffic_sensor_id: str
    traffic_congestion_level: int
    air_quality_sensor_id: str
    air_quality_index: int
    emergency_dispatch_id: str
    emergency_call_volume: int
    emergency_response_time_minutes: float
    public_transit_delay_minutes: float
    decision_priority_score: int
    status: str


def generate_city_telemetry(
    current_time: datetime | None = None,
    random_seed: int | None = None,
) -> list[dict[str, Any]]:
    """Return JSON-serializable telemetry records for all configured city sectors."""

    snapshot_time = current_time or datetime.now()
    randomizer = Random(random_seed)

    records = [
        _generate_sector_record(
            sector_index=sector_index,
            sector_name=sector_name,
            snapshot_time=snapshot_time,
            randomizer=randomizer,
        )
        for sector_index, sector_name in enumerate(CITY_SECTORS, start=1)
    ]

    return [asdict(record) for record in records]


def retrieve_relevant_telemetry(query: str, limit: int = 3) -> list[dict[str, Any]]:
    """Retrieve telemetry records matching a natural-language query.

    This is intentionally lightweight for the first scaffold. The future FastAPI
    agent endpoint can call this as its mock RAG retriever.
    """

    normalized_query = query.lower().strip()
    records = generate_city_telemetry()

    if not normalized_query:
        return []

    scored_records = [
        (record, _score_record_relevance(record, normalized_query)) for record in records
    ]
    relevant_records = [
        record
        for record, score in sorted(
            scored_records,
            key=lambda item: (
                item[1],
                item[0]["decision_priority_score"],
                item[0]["traffic_congestion_level"],
            ),
            reverse=True,
        )
        if score > 0
    ]

    return relevant_records[:limit]


def summarize_city_conditions(records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Produce aggregate telemetry for dashboard summary cards."""

    telemetry_records = records or generate_city_telemetry()
    record_count = len(telemetry_records)

    if record_count == 0:
        return {
            "average_congestion": 0,
            "average_aqi": 0,
            "average_response_time_minutes": 0,
            "total_emergency_call_volume": 0,
            "highest_priority_sector": None,
        }

    highest_priority_sector = max(
        telemetry_records, key=lambda record: record["decision_priority_score"]
    )

    return {
        "average_congestion": round(
            sum(record["traffic_congestion_level"] for record in telemetry_records)
            / record_count,
            1,
        ),
        "average_aqi": round(
            sum(record["air_quality_index"] for record in telemetry_records) / record_count,
            1,
        ),
        "average_response_time_minutes": round(
            sum(record["emergency_response_time_minutes"] for record in telemetry_records)
            / record_count,
            1,
        ),
        "total_emergency_call_volume": sum(
            record["emergency_call_volume"] for record in telemetry_records
        ),
        "highest_priority_sector": highest_priority_sector["sector_name"],
    }


def _generate_sector_record(
    sector_index: int,
    sector_name: str,
    snapshot_time: datetime,
    randomizer: Random,
) -> UrbanTelemetryRecord:
    profile = SECTOR_PROFILES[sector_name]
    rush_hour_multiplier = _calculate_rush_hour_multiplier(snapshot_time)
    traffic_noise = randomizer.uniform(-6.0, 6.0)

    congestion = _clamp_int(
        profile["traffic_baseline"] + rush_hour_multiplier + traffic_noise,
        minimum=0,
        maximum=100,
    )

    emergency_noise = randomizer.uniform(-3.0, 4.0)
    congestion_pressure = max(0, congestion - 55) * 0.08
    emergency_call_volume = _clamp_int(
        profile["emergency_baseline"] + emergency_noise + congestion_pressure,
        minimum=0,
        maximum=80,
    )

    call_volume_pressure = max(
        0,
        emergency_call_volume - profile["emergency_baseline"],
    )
    response_time_minutes = round(
        profile["response_baseline"]
        + (congestion * 0.025)
        + (call_volume_pressure * 0.11)
        + randomizer.uniform(-0.4, 0.5),
        1,
    )

    air_quality_index = _clamp_int(
        profile["aqi_baseline"]
        + (congestion * 0.22)
        + randomizer.uniform(-8.0, 10.0),
        minimum=20,
        maximum=250,
    )
    transit_delay_minutes = round(
        max(0, (congestion - 35) * 0.18 + randomizer.uniform(-1.5, 2.0)),
        1,
    )
    decision_priority_score = _clamp_int(
        (congestion * 0.38)
        + (air_quality_index * 0.22)
        + (response_time_minutes * 4.2)
        + (emergency_call_volume * 0.7),
        minimum=0,
        maximum=100,
    )

    return UrbanTelemetryRecord(
        sector_id=f"sector-{sector_index:02d}",
        sector_name=sector_name,
        timestamp=snapshot_time.isoformat(timespec="seconds"),
        traffic_sensor_id=f"Traffic Sensor-{sector_index:02d}",
        traffic_congestion_level=congestion,
        air_quality_sensor_id=f"AQI Sensor-{sector_index:02d}",
        air_quality_index=air_quality_index,
        emergency_dispatch_id=f"Emergency Dispatch-{sector_index:02d}",
        emergency_call_volume=emergency_call_volume,
        emergency_response_time_minutes=response_time_minutes,
        public_transit_delay_minutes=transit_delay_minutes,
        decision_priority_score=decision_priority_score,
        status=_classify_status(decision_priority_score),
    )


def _calculate_rush_hour_multiplier(snapshot_time: datetime) -> float:
    hour_as_decimal = snapshot_time.hour + (snapshot_time.minute / 60)
    morning_peak = _bell_curve(hour_as_decimal, peak_hour=8.75, width=0.75) * 26
    evening_peak = _bell_curve(hour_as_decimal, peak_hour=18.0, width=1.05) * 30
    return morning_peak + evening_peak


def _bell_curve(value: float, peak_hour: float, width: float) -> float:
    return exp(-((value - peak_hour) ** 2) / (2 * width**2))


def _score_record_relevance(record: dict[str, Any], normalized_query: str) -> int:
    score = 0
    query_terms = set(normalized_query.replace("-", " ").split())
    sector_terms = set(record["sector_name"].lower().replace("-", " ").split())

    score += len(query_terms.intersection(sector_terms)) * 3

    metric_keywords = {
        "traffic": ("traffic", "congestion", "road", "rush", "commute", "transit"),
        "air": ("air", "aqi", "pollution", "quality", "emissions"),
        "emergency": ("emergency", "ambulance", "dispatch", "response", "call"),
    }

    if any(keyword in normalized_query for keyword in metric_keywords["traffic"]):
        score += 2 if record["traffic_congestion_level"] >= 65 else 1
    if any(keyword in normalized_query for keyword in metric_keywords["air"]):
        score += 2 if record["air_quality_index"] >= 100 else 1
    if any(keyword in normalized_query for keyword in metric_keywords["emergency"]):
        score += 2 if record["emergency_response_time_minutes"] >= 9 else 1

    if "priority" in normalized_query or "risk" in normalized_query:
        score += 2 if record["decision_priority_score"] >= 70 else 1

    return score


def _classify_status(priority_score: int) -> str:
    if priority_score >= 78:
        return "critical"
    if priority_score >= 62:
        return "elevated"
    return "stable"


def _clamp_int(value: float, minimum: int, maximum: int) -> int:
    return round(max(minimum, min(maximum, value)))
