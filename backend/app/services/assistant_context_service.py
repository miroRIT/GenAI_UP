from __future__ import annotations

from typing import Any

from app.services.demo_evidence_service import evidence_for_question
from app.services.demo_scenario_service import scenario_catalog


def demo_assistant_response(question: str) -> dict[str, Any]:
    scenarios = _ranked_scenarios(question)
    evidence = evidence_for_question(question)
    top = scenarios[0]
    actions = []
    for scenario in scenarios[:3]:
        actions.extend([f"{scenario['district_name']}: {action}" for action in scenario["actions"][:2]])

    evidence_lines = [
        f"{record['district_name']} / {record['metric_name']}: {record['metric_value']} ({record['source_type']}, {record['freshness_minutes']} min old)"
        for record in evidence[:6]
    ]
    departments = sorted({scenario["recommended_department"] for scenario in scenarios[:3]})
    confidence = round(sum(record["confidence"] for record in evidence[:6]) / max(len(evidence[:6]), 1), 2)
    freshness = min(record["freshness_minutes"] for record in evidence) if evidence else 30

    answer = (
        f"Executive Summary: CivicIQ identifies {top['district_name']} as the highest-priority signal "
        f"with {top['risk_level']} {top['primary_risk']} risk ({top['risk_score']}/100). "
        f"Evidence Used: {'; '.join(evidence_lines)}. "
        f"Risk Level: {top['risk_level']}. "
        f"Recommended Actions: {'; '.join(actions[:5])}. "
        f"Responsible Departments: {', '.join(departments)}. "
        f"Confidence: {int(confidence * 100)}%. "
        f"Data Freshness: newest signal is {freshness} minutes old. "
        "Limitations: demo-mode evidence is seeded for a hackathon prototype and should be validated with official/live feeds before field action."
    )

    return {
        "answer": answer,
        "sources": [
            {"source": record["source_name"], "chunk_id": record["evidence_id"]}
            for record in evidence[:6]
        ],
        "related_metrics": [
            {
                "district_name": scenario["district_name"],
                "risk_score": scenario["risk_score"],
                "risk_level": scenario["risk_level"],
                "category": scenario["primary_risk"],
                "recommended_department": scenario["recommended_department"],
            }
            for scenario in scenarios[:3]
        ],
        "recommended_actions": actions[:6],
        "risk_or_opportunity_level": top["risk_level"],
        "data_limitations": [
            "Seeded NCR scenario data is used for reliable judging demos.",
            "Provider freshness and confidence are prototype indicators.",
            "Recommendations are decision support and require authorized human review.",
        ],
    }


def _ranked_scenarios(question: str) -> list[dict[str, Any]]:
    text = question.lower()
    scenarios = scenario_catalog()
    keyword_scores = {
        "gurugram-flood": ["gurugram", "flood", "waterlogging", "drainage"],
        "delhi-heat-aqi": ["delhi", "heat", "aqi", "health"],
        "noida-industrial-fire": ["noida", "industrial", "fire"],
        "ghaziabad-water-stress": ["ghaziabad", "water", "utility"],
        "meerut-storm-safety": ["meerut", "storm", "public safety"],
    }
    for scenario in scenarios:
        scenario["match_score"] = sum(1 for keyword in keyword_scores[scenario["scenario_id"]] if keyword in text)
    return sorted(scenarios, key=lambda item: (item["match_score"], item["risk_score"]), reverse=True)
