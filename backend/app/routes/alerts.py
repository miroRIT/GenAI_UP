from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.permissions import require_alert_access, require_auth, require_permissions
from app.models.db_models import User
from app.services.alert_service import (
    add_alert_note,
    assign_alert,
    create_alert,
    export_alerts_csv,
    generate_sla_summary,
    get_alert,
    get_alert_notes,
    get_timeline,
    list_alerts,
    escalate_alert,
    transition_alert,
    update_alert,
)
from app.services.pdf_service import build_incident_pdf


router = APIRouter(tags=["alerts"])


class AlertPayload(BaseModel):
    title: str
    description: str = ""
    district_id: str
    district_name: str
    category: str
    severity: str = "Medium"
    priority: str = "P3"
    assigned_department: str = "District Administration"
    source: str = "CivicIQ"
    recommended_actions: list[str] = []
    notes: str = ""


class AlertPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    severity: str | None = None
    priority: str | None = None
    status: str | None = None
    assigned_department: str | None = None
    notes: str | None = None
    recommended_actions: list[str] | None = None


class AssignPayload(BaseModel):
    department: str
    priority: str | None = None


class NotesPayload(BaseModel):
    notes: str = ""
    note_type: str = "Note"
    visibility: str = "Internal"


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return list_alerts(db)


@router.get("/alerts/assigned-to-me")
def assigned_to_me(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    alerts = list_alerts(db)
    if user.role == "Admin":
        return alerts
    return [
        alert
        for alert in alerts
        if alert["assigned_department"] == user.department
        or alert["district_id"] == user.district_id
    ]


@router.get("/alerts/sla-summary")
def sla_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    return generate_sla_summary(db)


@router.get("/alerts/export.csv")
def export_csv(
    db: Session = Depends(get_db),
    _user: User = Depends(require_permissions("reports:export")),
) -> Response:
    return Response(content=export_alerts_csv(db), media_type="text/csv")


@router.get("/alerts/{alert_id}")
def alert_detail(alert_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    data = update_response(alert)
    data["timeline"] = get_timeline(db, alert_id)
    data["notes_timeline"] = get_alert_notes(db, alert_id)
    return data


@router.post("/alerts")
def create(
    payload: AlertPayload,
    db: Session = Depends(get_db),
    user: User = Depends(require_permissions("*")),
) -> dict[str, object]:
    return create_alert(db, payload.model_dump(), actor=user.email)


@router.patch("/alerts/{alert_id}")
def patch_alert(
    alert_id: str,
    payload: AlertPatch,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "notes" if set(payload.model_dump(exclude_none=True)) == {"notes"} else "assign")
    return update_alert(db, alert, {key: value for key, value in payload.model_dump().items() if value is not None}, actor=user.email)


@router.post("/alerts/{alert_id}/assign")
def assign(
    alert_id: str,
    payload: AssignPayload,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "assign")
    return assign_alert(db, alert, payload.department, payload.priority, actor=user.email)


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id: str, payload: NotesPayload = NotesPayload(), db: Session = Depends(get_db), user: User = Depends(require_auth)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "acknowledge")
    return transition_alert(db, alert, "Acknowledged", actor=user.email, notes=payload.notes)


@router.post("/alerts/{alert_id}/resolve")
def resolve(alert_id: str, payload: NotesPayload = NotesPayload(), db: Session = Depends(get_db), user: User = Depends(require_auth)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "resolve")
    return transition_alert(db, alert, "Resolved", actor=user.email, notes=payload.notes)


@router.post("/alerts/{alert_id}/close")
def close(alert_id: str, payload: NotesPayload = NotesPayload(), db: Session = Depends(get_db), user: User = Depends(require_auth)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "close")
    return transition_alert(db, alert, "Closed", actor=user.email, notes=payload.notes)


@router.get("/alerts/{alert_id}/brief")
def brief(alert_id: str, db: Session = Depends(get_db), user: User = Depends(require_auth)) -> dict[str, str]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "export")
    return {"alert_id": alert_id, "brief": alert.incident_brief}


@router.get("/alerts/{alert_id}/export.md")
def export_markdown(alert_id: str, db: Session = Depends(get_db), user: User = Depends(require_auth)) -> Response:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "export")
    return Response(content=alert.incident_brief, media_type="text/markdown")


@router.get("/alerts/{alert_id}/export.pdf")
def export_pdf(alert_id: str, db: Session = Depends(get_db), user: User = Depends(require_auth)) -> Response:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "export")
    pdf_bytes = build_incident_pdf(db, alert, generated_by=user.email)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{alert_id}-incident-brief.pdf"'},
    )


@router.post("/alerts/{alert_id}/notes")
def add_note(alert_id: str, payload: NotesPayload, db: Session = Depends(get_db), user: User = Depends(require_auth)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "notes")
    return add_alert_note(db, alert, user, payload.notes, payload.note_type, payload.visibility)


@router.get("/alerts/{alert_id}/timeline")
def timeline(alert_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    _get_or_404(db, alert_id)
    return {"events": get_timeline(db, alert_id), "notes": get_alert_notes(db, alert_id)}


@router.post("/alerts/{alert_id}/escalate")
def escalate(alert_id: str, db: Session = Depends(get_db), user: User = Depends(require_auth)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    require_alert_access(user, alert, "resolve")
    return escalate_alert(db, alert, actor=user.email)


def _get_or_404(db: Session, alert_id: str):
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return alert


def update_response(alert):
    from app.services.alert_service import serialize_alert

    return serialize_alert(alert)
