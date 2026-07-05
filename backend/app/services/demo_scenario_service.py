from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.db_models import Alert
from app.services.alert_service import create_alert


DEMO_STORE = Path(os.getenv("DEMO_STORE_PATH", Path(__file__).resolve().parents[1] / "data" / "demo_runtime.json"))


def scenario_catalog() -> list[dict[str, Any]]:
    now = datetime.utcnow()
    return [
        {
            "scenario_id": "gurugram-flood",
            "title": "Gurugram Urban Flooding",
            "district_id": "NCR02",
            "district_name": "Gurugram",
            "primary_risk": "Flood",
            "risk_score": 91,
            "risk_level": "Critical",
            "latitude": 28.4595,
            "longitude": 77.0266,
            "updated_at": (now - timedelta(minutes=8)).isoformat() + "Z",
            "provider_mode": "Simulated feed",
            "summary": "Heavy rainfall, waterlogging complaints, utility disruption, and traffic delays are converging around Sector 29 and Golf Course Road.",
            "recommended_department": "Municipal Corporation",
            "expected_impact": "Reduce flood exposure for commuters and restore emergency route reliability within 4 hours.",
            "actions": ["Deploy drainage teams", "Activate traffic diversion", "Issue public waterlogging advisory"],
            "evidence": [
                {"source_type": "weather", "title": "Rainfall forecast", "value": "82 mm next 24 hours", "freshness": "8 minutes", "risk_contribution": 34},
                {"source_type": "citizen complaint", "title": "Waterlogging complaints", "value": "+240% vs baseline", "freshness": "12 minutes", "risk_contribution": 28},
                {"source_type": "traffic", "title": "Key route delay", "value": "38 minutes on NH-48 connector", "freshness": "5 minutes", "risk_contribution": 18},
                {"source_type": "utility", "title": "Pump station disruption", "value": "2 feeders unstable", "freshness": "18 minutes", "risk_contribution": 11},
            ],
        },
        {
            "scenario_id": "delhi-heat-aqi",
            "title": "Delhi Heatwave and AQI Health Risk",
            "district_id": "NCR01",
            "district_name": "Delhi NCT",
            "primary_risk": "AQI/Public Health",
            "risk_score": 88,
            "risk_level": "Critical",
            "latitude": 28.6139,
            "longitude": 77.209,
            "updated_at": (now - timedelta(minutes=11)).isoformat() + "Z",
            "provider_mode": "Simulated feed",
            "summary": "High feels-like temperature, poor AQI, and vulnerable population concentration indicate urgent public health risk.",
            "recommended_department": "Health Department",
            "expected_impact": "Lower heat illness exposure for vulnerable residents and pre-stage ambulance readiness.",
            "actions": ["Open cooling centers", "Issue AQI and heat advisory", "Pre-position ambulances near vulnerable clusters"],
            "evidence": [
                {"source_type": "weather", "title": "Feels-like index", "value": "47 C", "freshness": "11 minutes", "risk_contribution": 30},
                {"source_type": "environment", "title": "AQI", "value": "318 Very Poor", "freshness": "9 minutes", "risk_contribution": 26},
                {"source_type": "health", "title": "Vulnerable population flag", "value": "High senior and child exposure", "freshness": "25 minutes", "risk_contribution": 21},
            ],
        },
        {
            "scenario_id": "noida-industrial-fire",
            "title": "Noida Industrial Fire Preparedness Alert",
            "district_id": "NCR04",
            "district_name": "Gautam Buddh Nagar / Noida",
            "primary_risk": "Fire/Industrial",
            "risk_score": 78,
            "risk_level": "High",
            "latitude": 28.5355,
            "longitude": 77.391,
            "updated_at": (now - timedelta(minutes=14)).isoformat() + "Z",
            "provider_mode": "Simulated feed",
            "summary": "Heat stress, industrial zone density, recent incident reports, and response delay create elevated industrial fire risk.",
            "recommended_department": "Fire Department",
            "expected_impact": "Improve industrial incident readiness and reduce response delay in high-density manufacturing pockets.",
            "actions": ["Inspect high-risk industrial units", "Stage hazmat response", "Prepare evacuation checklist"],
            "evidence": [
                {"source_type": "manual scenario", "title": "Industrial zone marker", "value": "Sector 63/64 cluster", "freshness": "Demo seed", "risk_contribution": 24},
                {"source_type": "incident", "title": "Recent fire incident", "value": "1 warehouse smoke report", "freshness": "19 minutes", "risk_contribution": 19},
                {"source_type": "emergency", "title": "Response delay", "value": "13.5 min vs 9 min target", "freshness": "16 minutes", "risk_contribution": 18},
            ],
        },
        {
            "scenario_id": "ghaziabad-water-stress",
            "title": "Ghaziabad Water Stress and Utility Disruption",
            "district_id": "NCR03",
            "district_name": "Ghaziabad",
            "primary_risk": "Drought/Water Stress",
            "risk_score": 74,
            "risk_level": "High",
            "latitude": 28.6692,
            "longitude": 77.4538,
            "updated_at": (now - timedelta(minutes=18)).isoformat() + "Z",
            "provider_mode": "Simulated feed",
            "summary": "Water shortage complaints, power outage reports, and rising temperature indicate a near-term utility stress event.",
            "recommended_department": "Water Department",
            "expected_impact": "Prioritize water tanker routing and utility repair before complaints become a public order issue.",
            "actions": ["Deploy tankers", "Prioritize feeder repair", "Publish ward-level water schedule"],
            "evidence": [
                {"source_type": "citizen complaint", "title": "Water shortage complaints", "value": "+170% vs baseline", "freshness": "18 minutes", "risk_contribution": 27},
                {"source_type": "utility", "title": "Power outage reports", "value": "14 open reports", "freshness": "21 minutes", "risk_contribution": 19},
                {"source_type": "weather", "title": "Temperature trend", "value": "43 C and rising", "freshness": "13 minutes", "risk_contribution": 16},
            ],
        },
        {
            "scenario_id": "meerut-storm-safety",
            "title": "Meerut Storm Response and Road Clearance Alert",
            "district_id": "NCR06",
            "district_name": "Meerut",
            "primary_risk": "Public Safety",
            "risk_score": 69,
            "risk_level": "High",
            "latitude": 28.9845,
            "longitude": 77.7064,
            "updated_at": (now - timedelta(minutes=6)).isoformat() + "Z",
            "provider_mode": "Simulated feed",
            "summary": "Thunderstorm alert, road blockage, and emergency incidents require public safety coordination.",
            "recommended_department": "District Administration",
            "expected_impact": "Maintain route access for emergency vehicles and reduce citizen exposure during storm window.",
            "actions": ["Activate emergency control room", "Dispatch road clearance crew", "Issue citizen storm advisory"],
            "evidence": [
                {"source_type": "weather", "title": "Thunderstorm alert", "value": "60-70 km/h gust potential", "freshness": "6 minutes", "risk_contribution": 25},
                {"source_type": "traffic", "title": "Road blockage", "value": "2 arterial disruptions", "freshness": "10 minutes", "risk_contribution": 17},
                {"source_type": "emergency", "title": "Incident load", "value": "9 active calls", "freshness": "7 minutes", "risk_contribution": 15},
            ],
        },
    ]


def run_crisis_demo(db: Session, actor: str = "demo") -> dict[str, Any]:
    scenarios = scenario_catalog()
    created_alerts = []
    for scenario in scenarios:
        existing = db.query(Alert).filter(Alert.title == scenario["title"]).first()
        if existing:
            created_alerts.append(existing.alert_id)
            continue
        alert = create_alert(
            db,
            {
                "title": scenario["title"],
                "description": scenario["summary"],
                "district_id": scenario["district_id"],
                "district_name": scenario["district_name"],
                "category": scenario["primary_risk"],
                "severity": scenario["risk_level"],
                "priority": "P1" if scenario["risk_level"] == "Critical" else "P2",
                "assigned_department": scenario["recommended_department"],
                "source": "CivicIQ Demo Scenario Engine",
                "recommended_actions": scenario["actions"],
            },
            actor=actor,
        )
        created_alerts.append(alert["alert_id"])
    runtime = _default_runtime(scenarios)
    runtime["demo_active"] = True
    runtime["activated_at"] = datetime.utcnow().isoformat() + "Z"
    runtime["created_alert_ids"] = created_alerts
    _write_runtime(runtime)
    return {"message": "NCR crisis demo activated.", "scenario_count": len(scenarios), "alert_ids": created_alerts, "next_steps": demo_checklist()}


def reset_demo_runtime() -> dict[str, Any]:
    runtime = _default_runtime(scenario_catalog())
    _write_runtime(runtime)
    return runtime


def demo_dashboard_overview() -> dict[str, Any]:
    runtime = _read_runtime()
    scenarios = runtime["scenarios"]
    critical = [item for item in scenarios if item["risk_level"] == "Critical"]
    high_or_critical = [item for item in scenarios if item["risk_level"] in {"High", "Critical"}]
    return {
        "region_name": "National Capital Region, India",
        "tagline": "AI Decision Intelligence for NCR Disaster & Community Resilience",
        "demo_active": runtime.get("demo_active", False),
        "overall_risk_score": 82,
        "active_critical_alerts": len(critical),
        "districts_at_high_or_critical_risk": len(high_or_critical),
        "provider_health": "4/4 simulated feeds healthy",
        "average_aqi": 286,
        "weather_alerts": 3,
        "traffic_disruption_index": 77,
        "emergency_response_load": "High",
        "open_department_actions": 14,
        "last_updated": runtime.get("activated_at") or runtime.get("last_seeded_at"),
        "why_this_matters": "CivicIQ turns fragmented weather, traffic, civic complaints, and incident signals into explainable action plans for NCR authorities.",
        "scenarios": scenarios,
    }


def demo_recommendations() -> list[dict[str, Any]]:
    return [
        {
            "recommendation_id": scenario["scenario_id"],
            "title": f"{scenario['actions'][0]} for {scenario['district_name']}",
            "district_name": scenario["district_name"],
            "risk_level": scenario["risk_level"],
            "confidence_score": 0.93 if scenario["risk_level"] == "Critical" else 0.86,
            "suggested_department": scenario["recommended_department"],
            "expected_impact": scenario["expected_impact"],
            "actions": scenario["actions"],
        }
        for scenario in _read_runtime()["scenarios"]
    ]


def explain_recommendation(recommendation_id: str) -> dict[str, Any] | None:
    scenario = next((item for item in _read_runtime()["scenarios"] if item["scenario_id"] == recommendation_id), None)
    if not scenario:
        return None
    return {
        "recommendation_id": recommendation_id,
        "title": f"{scenario['actions'][0]} for {scenario['district_name']}",
        "why_generated": scenario["summary"],
        "evidence_records": scenario["evidence"],
        "related_data_points": [
            {"metric": "Risk score", "value": f"{scenario['risk_score']}/100"},
            {"metric": "Risk level", "value": scenario["risk_level"]},
            {"metric": "Data freshness", "value": _freshness_label(scenario["updated_at"])},
        ],
        "source_mix": sorted({evidence["source_type"] for evidence in scenario["evidence"]}),
        "confidence_score": 0.93 if scenario["risk_level"] == "Critical" else 0.86,
        "risk_contribution": sum(int(evidence["risk_contribution"]) for evidence in scenario["evidence"]),
        "suggested_department": scenario["recommended_department"],
        "expected_impact": scenario["expected_impact"],
        "limitation_note": "Demo mode uses realistic seeded NCR telemetry. Production should replace simulated feeds with official/live providers.",
    }


def provider_health_demo() -> list[dict[str, Any]]:
    live_hint = "Live if configured, simulated otherwise"
    return [
        {"provider": "IMD", "status": "Simulated", "freshness": "Updated 6 minutes ago", "sample_payload": "Thunderstorm and rainfall alerts", "mode": live_hint},
        {"provider": "OpenWeather", "status": "Simulated", "freshness": "Updated 11 minutes ago", "sample_payload": "Heat index and rainfall forecast", "mode": live_hint},
        {"provider": "NewsAPI/GDELT", "status": "Simulated", "freshness": "Updated 18 minutes ago", "sample_payload": "NCR civic and incident scan", "mode": live_hint},
        {"provider": "Traffic", "status": "Simulated", "freshness": "Updated 5 minutes ago", "sample_payload": "Congestion and road blockage signals", "mode": live_hint},
    ]


def operations_snapshot() -> dict[str, Any]:
    runtime = _read_runtime()
    return {
        "api_status": "Healthy",
        "provider_health": provider_health_demo(),
        "job_health": [
            {"job": "Weather Refresh", "status": "Success", "records": 16, "retry_count": 0, "dead_letter_count": 0},
            {"job": "News Scan", "status": "Warning", "records": 9, "retry_count": 1, "dead_letter_count": 0},
            {"job": "Traffic Refresh", "status": "Success", "records": 11, "retry_count": 0, "dead_letter_count": 0},
            {"job": "Risk Recalculation", "status": "Success", "records": 11, "retry_count": 0, "dead_letter_count": 0},
            {"job": "Alert Generation", "status": "Success", "records": len(runtime.get("created_alert_ids", [])), "retry_count": 0, "dead_letter_count": 0},
        ],
        "average_response_time_ms": 128,
        "queue_depth": 7,
        "dead_letter_count": 1,
        "last_ingestion_run": runtime.get("activated_at") or runtime.get("last_seeded_at"),
        "events": audit_logs(),
    }


def audit_logs() -> list[dict[str, Any]]:
    runtime = _read_runtime()
    return runtime.get("audit_logs", [])


def refresh_demo_feeds() -> dict[str, Any]:
    runtime = _read_runtime()
    event = {
        "event_id": f"audit-{len(runtime.get('audit_logs', [])) + 1}",
        "actor": "demo-operator",
        "action": "scenario refreshed",
        "target": "NCR demo feeds",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "Success",
    }
    runtime.setdefault("audit_logs", []).insert(0, event)
    runtime["last_seeded_at"] = event["created_at"]
    _write_runtime(runtime)
    return {"message": "Demo feeds refreshed.", "jobs": operations_snapshot()["job_health"], "audit_event": event}


def map_layers() -> dict[str, Any]:
    scenarios = _read_runtime()["scenarios"]
    return {
        "boundary_source": {
            "source_type": "demo",
            "source_name": "NCR district boundary approximation",
            "production_source_options": ["Bhuvan", "NCR Planning Board", "Survey of India", "state GIS portals"],
        },
        "incidents": [
            {
                "incident_id": scenario["scenario_id"],
                "title": scenario["title"],
                "district_name": scenario["district_name"],
                "risk_level": scenario["risk_level"],
                "risk_score": scenario["risk_score"],
                "category": scenario["primary_risk"],
                "latitude": scenario["latitude"],
                "longitude": scenario["longitude"],
                "updated_at": scenario["updated_at"],
            }
            for scenario in scenarios
        ],
    }


def exports_list() -> list[dict[str, Any]]:
    scenarios = _read_runtime()["scenarios"]
    return [
        {
            "export_id": scenario["scenario_id"],
            "title": f"{scenario['district_name']} incident brief",
            "format": "markdown",
            "storage_mode": "local-demo",
            "download_url": f"/api/exports/{scenario['scenario_id']}",
            "expires_in_minutes": 60,
            "created_at": scenario["updated_at"],
        }
        for scenario in scenarios
    ]


def crisis_summary() -> dict[str, Any]:
    overview = demo_dashboard_overview()
    scenarios = sorted(overview["scenarios"], key=lambda item: item["risk_score"], reverse=True)
    top_three = scenarios[:3]
    departments = sorted({scenario["recommended_department"] for scenario in top_three})
    highest = top_three[0]
    summary_text = (
        "CivicIQ detected a Critical NCR resilience situation driven by "
        f"{top_three[0]['district_name']} {top_three[0]['primary_risk'].lower()}, "
        f"{top_three[1]['district_name']} {top_three[1]['primary_risk'].lower()} risk, and "
        f"{top_three[2]['district_name']} {top_three[2]['primary_risk'].lower()} exposure. "
        "Immediate focus is recommended on drainage response, public health advisories, and emergency readiness."
    )
    return {
        "title": "NCR Crisis Summary",
        "timestamp": overview["last_updated"],
        "overall_risk_level": "Critical",
        "top_affected_districts": [scenario["district_name"] for scenario in top_three],
        "active_critical_alerts": overview["active_critical_alerts"],
        "highest_risk_scenario": highest["title"],
        "top_recommended_action": highest["actions"][0],
        "departments_involved": departments,
        "ai_confidence": 0.91,
        "data_freshness": "5-18 minutes",
        "executive_summary": summary_text,
        "markdown": (
            f"# NCR Crisis Summary\n\n"
            f"- Overall risk: Critical\n"
            f"- Top districts: {', '.join(scenario['district_name'] for scenario in top_three)}\n"
            f"- Critical alerts: {overview['active_critical_alerts']}\n"
            f"- Top action: {highest['actions'][0]}\n\n"
            f"{summary_text}\n"
        ),
    }


def export_brief(export_id: str) -> str | None:
    scenario = next((item for item in _read_runtime()["scenarios"] if item["scenario_id"] == export_id), None)
    if not scenario:
        return None
    evidence = "\n".join(f"- {item['title']}: {item['value']} ({item['freshness']})" for item in scenario["evidence"])
    actions = "\n".join(f"- {action}" for action in scenario["actions"])
    return f"""# CivicIQ Incident Brief: {scenario['title']}

District: {scenario['district_name']}
Risk Level: {scenario['risk_level']}
Risk Score: {scenario['risk_score']}/100
Suggested Department: {scenario['recommended_department']}
Storage Mode: local-demo

## Situation
{scenario['summary']}

## Evidence
{evidence}

## Recommended Actions
{actions}

## Responsible AI Note
This is a demo-mode decision-support brief based on seeded NCR telemetry. Production deployments should validate actions with official authorities and live provider data.
"""


def demo_checklist() -> list[dict[str, Any]]:
    return [
        {"step": 1, "label": "NCR overview risk rises", "status": "Ready"},
        {"step": 2, "label": "Gurugram flood alert becomes Critical", "status": "Ready"},
        {"step": 3, "label": "AI explains weather, complaints, and traffic evidence", "status": "Ready"},
        {"step": 4, "label": "Officer assigns alert to Municipal Corporation", "status": "Ready"},
        {"step": 5, "label": "Incident brief is exported", "status": "Ready"},
        {"step": 6, "label": "Dashboard shows response status", "status": "Ready"},
    ]


def _default_runtime(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "demo_active": False,
        "last_seeded_at": now,
        "activated_at": None,
        "created_alert_ids": [],
        "scenarios": scenarios,
        "audit_logs": [
            {"event_id": "audit-1", "actor": "admin@civiciq.demo", "action": "login", "target": "Demo console", "created_at": now, "status": "Success"},
            {"event_id": "audit-2", "actor": "officer@civiciq.demo", "action": "alert acknowledged", "target": "Gurugram flood scenario", "created_at": now, "status": "Simulated"},
            {"event_id": "audit-3", "actor": "analyst@civiciq.demo", "action": "brief exported", "target": "Delhi heatwave advisory", "created_at": now, "status": "Simulated"},
        ],
    }


def _read_runtime() -> dict[str, Any]:
    if not DEMO_STORE.exists():
        reset_demo_runtime()
    return json.loads(DEMO_STORE.read_text(encoding="utf-8"))


def _write_runtime(payload: dict[str, Any]) -> None:
    DEMO_STORE.parent.mkdir(parents=True, exist_ok=True)
    DEMO_STORE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _freshness_label(updated_at: str) -> str:
    try:
        timestamp = datetime.fromisoformat(updated_at.replace("Z", ""))
        minutes = max(1, int((datetime.utcnow() - timestamp).total_seconds() / 60))
        return f"{minutes} minutes"
    except Exception:
        return "Demo seed"
