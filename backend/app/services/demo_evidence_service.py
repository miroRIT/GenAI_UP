from __future__ import annotations

from typing import Any

from app.services.demo_scenario_service import scenario_catalog


def seeded_evidence_records() -> list[dict[str, Any]]:
    records = []
    for scenario in scenario_catalog():
        for index, evidence in enumerate(scenario["evidence"], start=1):
            records.append(
                {
                    "evidence_id": f"{scenario['scenario_id']}-e{index}",
                    "scenario_id": scenario["scenario_id"],
                    "district_id": scenario["district_id"],
                    "district_name": scenario["district_name"],
                    "category": scenario["primary_risk"],
                    "metric_name": evidence["title"],
                    "metric_value": evidence["value"],
                    "baseline_value": _baseline_for(evidence["title"]),
                    "source_type": evidence["source_type"],
                    "source_name": f"CivicIQ {evidence['source_type'].title()} Demo Feed",
                    "freshness_minutes": _freshness_minutes(evidence["freshness"]),
                    "confidence": 0.93 if scenario["risk_level"] == "Critical" else 0.86,
                    "risk_contribution": evidence["risk_contribution"],
                    "explanation": f"{evidence['title']} contributes to {scenario['risk_level']} {scenario['primary_risk']} risk in {scenario['district_name']}.",
                }
            )
    return records


def evidence_for_question(question: str) -> list[dict[str, Any]]:
    text = question.lower()
    records = seeded_evidence_records()
    scenario_keywords = {
        "gurugram-flood": ["gurugram", "flood", "waterlogging", "drainage"],
        "delhi-heat-aqi": ["delhi", "heat", "aqi", "health", "cooling"],
        "noida-industrial-fire": ["noida", "industrial", "fire", "hazmat"],
        "ghaziabad-water-stress": ["ghaziabad", "water", "utility", "outage"],
        "meerut-storm-safety": ["meerut", "storm", "road", "public safety"],
    }
    matched_scenarios = [
        scenario_id
        for scenario_id, keywords in scenario_keywords.items()
        if any(keyword in text for keyword in keywords)
    ]
    if "next 24" in text or "priority" in text or "leadership" in text or "ncr crisis" in text:
        matched_scenarios = list(scenario_keywords)
    if not matched_scenarios:
        matched_scenarios = ["gurugram-flood", "delhi-heat-aqi", "noida-industrial-fire"]
    return [record for record in records if record["scenario_id"] in matched_scenarios][:8]


def _freshness_minutes(label: str) -> int:
    try:
        return int(label.split()[0])
    except Exception:
        return 30


def _baseline_for(metric_name: str) -> str:
    baselines = {
        "Rainfall forecast": "20 mm/day advisory threshold",
        "Waterlogging complaints": "Normal complaint baseline",
        "Key route delay": "12 minute normal delay",
        "Feels-like index": "40 C heat advisory threshold",
        "AQI": "200 poor-air threshold",
        "Response delay": "9 minute response target",
    }
    return baselines.get(metric_name, "Local operating baseline")
