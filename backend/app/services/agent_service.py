from __future__ import annotations

from typing import Any

from app.services.mock_data_service import retrieve_relevant_telemetry


SYSTEM_CONTEXT = """
You are an Urban Decision Intelligence Assistant.
Your role is to interpret city telemetry, identify operational risk,
and provide concise recommendations for civic decision makers.
Base answers only on available telemetry records.
""".strip()


def answer_urban_intelligence_query(query: str) -> dict[str, Any]:
    normalized_query = query.strip()
    relevant_records = retrieve_relevant_telemetry(normalized_query)
    data_focus = _infer_data_focus(normalized_query)

    if not relevant_records:
        topic = data_focus if data_focus != "general urban operations" else normalized_query
        return {
            "answer": (
                f"I don't have enough data on {topic}—would you like me to simulate "
                "a projection based on historical trends?"
            ),
            "data_focus": data_focus,
            "confidence_score": 0.38,
            "system_context": SYSTEM_CONTEXT,
            "records": [],
        }

    highest_priority_record = max(
        relevant_records,
        key=lambda record: record["decision_priority_score"],
    )

    answer = _compose_answer(highest_priority_record, len(relevant_records))

    return {
        "answer": answer,
        "data_focus": data_focus,
        "confidence_score": _calculate_confidence_score(relevant_records),
        "system_context": SYSTEM_CONTEXT,
        "records": relevant_records,
    }


def _compose_answer(record: dict[str, Any], record_count: int) -> str:
    return (
        f"{record['sector_name']} is the current intervention priority. "
        f"Congestion is at {record['traffic_congestion_level']}%, AQI is "
        f"{record['air_quality_index']}, emergency calls are at "
        f"{record['emergency_call_volume']}, and response time is "
        f"{record['emergency_response_time_minutes']} minutes. "
        f"Review signal timing, dispatch staging, and transit flow controls across "
        f"the {record_count} most relevant telemetry record(s)."
    )


def _infer_data_focus(query: str) -> str:
    normalized_query = query.lower()

    if any(term in normalized_query for term in ("traffic", "congestion", "road", "transit")):
        return "traffic congestion"
    if any(term in normalized_query for term in ("air", "aqi", "pollution", "emissions")):
        return "air quality"
    if any(term in normalized_query for term in ("emergency", "dispatch", "response", "ambulance")):
        return "emergency services"
    if any(term in normalized_query for term in ("risk", "priority", "intervention")):
        return "city intervention priority"

    return "general urban operations"


def _calculate_confidence_score(records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0

    record_count_boost = min(len(records) * 0.08, 0.24)
    priority_signal = max(record["decision_priority_score"] for record in records) / 100
    return round(min(0.95, 0.62 + record_count_boost + (priority_signal * 0.12)), 2)
