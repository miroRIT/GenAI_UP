from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.db_models import Alert, AlertNote, AlertTimelineEvent, User
from app.services.disaster_risk_engine import calculate_disaster_risk


DEFAULT_DEPARTMENT_BY_CATEGORY = {
    "Flood": "Disaster Management Authority",
    "Heatwave": "Health Department",
    "AQI/Public Health": "Pollution Control Board",
    "Traffic": "Traffic Police",
    "Fire/Industrial": "Fire Department",
    "Utility": "Electricity Utility",
    "Healthcare": "Health Department",
    "Public Safety": "District Administration",
    "Weather": "Disaster Management Authority",
    "News-Derived Incident": "District Administration",
}


def seed_alerts(db: Session) -> None:
    if db.query(Alert).count() > 0:
        return
    for risk in calculate_disaster_risk()[:8]:
        top_risk_name, top_risk = max(risk["risks"].items(), key=lambda item: item[1]["score"])
        if top_risk["score"] < 45:
            continue
        category = _category_from_risk(top_risk_name)
        create_alert(
            db,
            {
                "title": f"{category} watch: {risk['district_name']}",
                "description": top_risk["explanation"],
                "district_id": risk["district_id"],
                "district_name": risk["district_name"],
                "category": category,
                "severity": top_risk["level"],
                "priority": priority_from_severity(top_risk["level"]),
                "assigned_department": DEFAULT_DEPARTMENT_BY_CATEGORY.get(category, "District Administration"),
                "source": "CivicIQ Risk Engine",
                "recommended_actions": top_risk["recommended_actions"],
            },
            actor="system",
        )


def list_alerts(db: Session) -> list[dict[str, object]]:
    return [serialize_alert(alert) for alert in db.query(Alert).order_by(Alert.created_at.desc()).all()]


def get_alert(db: Session, alert_id: str) -> Alert | None:
    return db.query(Alert).filter(Alert.alert_id == alert_id).first()


def create_alert(db: Session, payload: dict[str, object], actor: str = "system") -> dict[str, object]:
    priority = str(payload.get("priority", priority_from_severity(str(payload.get("severity", "Medium")))))
    now = datetime.utcnow()
    first_response_due_at, resolution_due_at = sla_due_times(now, priority)
    alert = Alert(
        alert_id=str(payload.get("alert_id") or f"AL-{uuid4().hex[:8].upper()}"),
        title=str(payload["title"]),
        description=str(payload.get("description", "")),
        district_id=str(payload["district_id"]),
        district_name=str(payload["district_name"]),
        category=str(payload["category"]),
        severity=str(payload.get("severity", "Medium")),
        priority=priority,
        status=str(payload.get("status", "New")),
        assigned_department=str(payload.get("assigned_department", DEFAULT_DEPARTMENT_BY_CATEGORY.get(str(payload["category"]), "District Administration"))),
        source=str(payload.get("source", "CivicIQ")),
        recommended_actions=json.dumps(payload.get("recommended_actions", [])),
        notes=str(payload.get("notes", "")),
        first_response_due_at=first_response_due_at,
        resolution_due_at=resolution_due_at,
        sla_due_at=resolution_due_at,
        sla_status="On Track",
        escalation_status="None",
    )
    alert.incident_brief = generate_incident_brief(alert)
    db.add(alert)
    db.commit()
    add_timeline(db, alert.alert_id, "created", "Alert created.", actor)
    return serialize_alert(alert)


def update_alert(db: Session, alert: Alert, payload: dict[str, object], actor: str = "system") -> dict[str, object]:
    for field in ["title", "description", "category", "severity", "priority", "status", "assigned_department", "notes"]:
        if field in payload:
            setattr(alert, field, str(payload[field]))
    if "recommended_actions" in payload:
        alert.recommended_actions = json.dumps(payload["recommended_actions"])
    alert.updated_at = datetime.utcnow()
    alert.incident_brief = generate_incident_brief(alert)
    db.commit()
    add_timeline(db, alert.alert_id, "updated", "Alert updated.", actor)
    return serialize_alert(alert)


def assign_alert(db: Session, alert: Alert, department: str, priority: str | None = None, actor: str = "system") -> dict[str, object]:
    alert.assigned_department = department
    if priority:
        alert.priority = priority
    alert.status = "In Progress"
    alert.updated_at = datetime.utcnow()
    alert.incident_brief = generate_incident_brief(alert)
    db.commit()
    add_timeline(db, alert.alert_id, "assigned", f"Assigned to {department}.", actor)
    return serialize_alert(alert)


def transition_alert(db: Session, alert: Alert, status: str, actor: str = "system", notes: str = "") -> dict[str, object]:
    alert.status = status
    alert.updated_at = datetime.utcnow()
    if notes:
        alert.notes = f"{alert.notes}\n{notes}".strip()
    if status == "Acknowledged":
        alert.acknowledged_at = datetime.utcnow()
    if status == "Resolved":
        alert.resolved_at = datetime.utcnow()
    refresh_sla_status(alert)
    alert.incident_brief = generate_incident_brief(alert)
    db.commit()
    add_timeline(db, alert.alert_id, status.lower().replace(" ", "_"), f"Status changed to {status}.", actor)
    return serialize_alert(alert)


def add_alert_note(
    db: Session,
    alert: Alert,
    user: User,
    note_text: str,
    note_type: str = "Note",
    visibility: str = "Internal",
) -> dict[str, object]:
    note = AlertNote(
        alert_id=alert.alert_id,
        user_id=user.id,
        note_text=note_text,
        note_type=note_type,
        visibility=visibility,
    )
    db.add(note)
    db.commit()
    add_timeline(db, alert.alert_id, "note_added", note_text, user.email)
    return serialize_note(note)


def get_alert_notes(db: Session, alert_id: str) -> list[dict[str, object]]:
    notes = db.query(AlertNote).filter(AlertNote.alert_id == alert_id).order_by(AlertNote.created_at).all()
    return [serialize_note(note) for note in notes]


def serialize_note(note: AlertNote) -> dict[str, object]:
    return {
        "note_id": note.note_id,
        "alert_id": note.alert_id,
        "user_id": note.user_id,
        "note_text": note.note_text,
        "note_type": note.note_type,
        "visibility": note.visibility,
        "created_at": note.created_at.isoformat(),
    }


def sla_due_times(created_at: datetime, priority: str) -> tuple[datetime, datetime]:
    rules = {
        "P1": (timedelta(minutes=15), timedelta(hours=4)),
        "P2": (timedelta(minutes=30), timedelta(hours=8)),
        "P3": (timedelta(hours=2), timedelta(hours=24)),
        "P4": (timedelta(hours=8), timedelta(hours=72)),
    }
    first_response_delta, resolution_delta = rules.get(priority, rules["P3"])
    return created_at + first_response_delta, created_at + resolution_delta


def refresh_sla_status(alert: Alert) -> None:
    now = datetime.utcnow()
    if alert.status in {"Resolved", "Closed"}:
        alert.sla_status = "On Track"
        return
    if alert.resolution_due_at and now > alert.resolution_due_at:
        alert.sla_status = "Breached"
    elif alert.first_response_due_at and not alert.acknowledged_at and now > alert.first_response_due_at:
        alert.sla_status = "At Risk"
    else:
        alert.sla_status = "On Track"


def escalate_alert(db: Session, alert: Alert, actor: str = "system") -> dict[str, object]:
    refresh_sla_status(alert)
    alert.escalation_status = "Escalated to Admin and District Officer"
    alert.updated_at = datetime.utcnow()
    db.commit()
    add_timeline(db, alert.alert_id, "escalated", alert.escalation_status, actor)
    return serialize_alert(alert)


def generate_sla_summary(db: Session) -> dict[str, object]:
    alerts = db.query(Alert).all()
    summary = {"On Track": 0, "At Risk": 0, "Breached": 0}
    for alert in alerts:
        refresh_sla_status(alert)
        summary[alert.sla_status] = summary.get(alert.sla_status, 0) + 1
    db.commit()
    return {"summary": summary, "total": len(alerts)}


def add_timeline(db: Session, alert_id: str, event_type: str, message: str, actor: str) -> None:
    db.add(AlertTimelineEvent(alert_id=alert_id, event_type=event_type, message=message, actor=actor))
    db.commit()


def get_timeline(db: Session, alert_id: str) -> list[dict[str, object]]:
    events = db.query(AlertTimelineEvent).filter(AlertTimelineEvent.alert_id == alert_id).order_by(AlertTimelineEvent.created_at).all()
    return [
        {
            "event_type": event.event_type,
            "message": event.message,
            "actor": event.actor,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]


def serialize_alert(alert: Alert) -> dict[str, object]:
    return {
        "alert_id": alert.alert_id,
        "title": alert.title,
        "description": alert.description,
        "district_id": alert.district_id,
        "district_name": alert.district_name,
        "category": alert.category,
        "severity": alert.severity,
        "priority": alert.priority,
        "status": alert.status,
        "assigned_department": alert.assigned_department,
        "source": alert.source,
        "created_at": alert.created_at.isoformat(),
        "updated_at": alert.updated_at.isoformat(),
        "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "sla_due_at": alert.sla_due_at.isoformat() if alert.sla_due_at else None,
        "sla_status": alert.sla_status,
        "first_response_due_at": alert.first_response_due_at.isoformat() if alert.first_response_due_at else None,
        "resolution_due_at": alert.resolution_due_at.isoformat() if alert.resolution_due_at else None,
        "escalation_status": alert.escalation_status,
        "recommended_actions": json.loads(alert.recommended_actions or "[]"),
        "notes": alert.notes,
        "incident_brief": alert.incident_brief,
    }


def generate_incident_brief(alert: Alert) -> str:
    actions = "\n".join(f"- {action}" for action in json.loads(alert.recommended_actions or "[]"))
    return f"""# Incident Brief: {alert.title}

District: {alert.district_name}
Category: {alert.category}
Severity: {alert.severity}
Priority: {alert.priority}
Assigned Department: {alert.assigned_department}
Status: {alert.status}
Generated: {datetime.utcnow().isoformat(timespec="seconds")}Z

## Situation Summary
{alert.description}

## Evidence and Source
Source: {alert.source}

## Recommended Immediate Actions
{actions or "- Validate signal and assign field verification."}

## Notes
{alert.notes or "No notes recorded."}

AI-generated recommendations are decision support only and must be validated by official authorities.
"""


def export_alerts_csv(db: Session) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["alert_id", "title", "district_name", "category", "severity", "priority", "status", "assigned_department"],
    )
    writer.writeheader()
    for alert in list_alerts(db):
        writer.writerow({field: alert[field] for field in writer.fieldnames})
    return output.getvalue()


def priority_from_severity(severity: str) -> str:
    return {"Critical": "P1", "High": "P2", "Medium": "P3", "Low": "P4"}.get(severity, "P3")


def _category_from_risk(risk_name: str) -> str:
    return {
        "flood": "Flood",
        "heatwave": "Heatwave",
        "aqi_public_health": "AQI/Public Health",
        "industrial_fire": "Fire/Industrial",
        "drought_water_stress": "Utility",
        "seismic": "Public Safety",
    }[risk_name]
