from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.alert_service import (
    assign_alert,
    create_alert,
    export_alerts_csv,
    get_alert,
    get_timeline,
    list_alerts,
    transition_alert,
    update_alert,
)


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


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return list_alerts(db)


@router.get("/alerts/export.csv")
def export_csv(db: Session = Depends(get_db)) -> Response:
    return Response(content=export_alerts_csv(db), media_type="text/csv")


@router.get("/alerts/{alert_id}")
def alert_detail(alert_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    data = update_response(alert)
    data["timeline"] = get_timeline(db, alert_id)
    return data


@router.post("/alerts")
def create(payload: AlertPayload, db: Session = Depends(get_db)) -> dict[str, object]:
    return create_alert(db, payload.model_dump(), actor="api")


@router.patch("/alerts/{alert_id}")
def patch_alert(alert_id: str, payload: AlertPatch, db: Session = Depends(get_db)) -> dict[str, object]:
    alert = _get_or_404(db, alert_id)
    return update_alert(db, alert, {key: value for key, value in payload.model_dump().items() if value is not None}, actor="api")


@router.post("/alerts/{alert_id}/assign")
def assign(alert_id: str, payload: AssignPayload, db: Session = Depends(get_db)) -> dict[str, object]:
    return assign_alert(db, _get_or_404(db, alert_id), payload.department, payload.priority, actor="api")


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id: str, payload: NotesPayload = NotesPayload(), db: Session = Depends(get_db)) -> dict[str, object]:
    return transition_alert(db, _get_or_404(db, alert_id), "Acknowledged", actor="api", notes=payload.notes)


@router.post("/alerts/{alert_id}/resolve")
def resolve(alert_id: str, payload: NotesPayload = NotesPayload(), db: Session = Depends(get_db)) -> dict[str, object]:
    return transition_alert(db, _get_or_404(db, alert_id), "Resolved", actor="api", notes=payload.notes)


@router.post("/alerts/{alert_id}/close")
def close(alert_id: str, payload: NotesPayload = NotesPayload(), db: Session = Depends(get_db)) -> dict[str, object]:
    return transition_alert(db, _get_or_404(db, alert_id), "Closed", actor="api", notes=payload.notes)


@router.get("/alerts/{alert_id}/brief")
def brief(alert_id: str, db: Session = Depends(get_db)) -> dict[str, str]:
    return {"alert_id": alert_id, "brief": _get_or_404(db, alert_id).incident_brief}


@router.get("/alerts/{alert_id}/export.md")
def export_markdown(alert_id: str, db: Session = Depends(get_db)) -> Response:
    alert = _get_or_404(db, alert_id)
    return Response(content=alert.incident_brief, media_type="text/markdown")


def _get_or_404(db: Session, alert_id: str):
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return alert


def update_response(alert):
    from app.services.alert_service import serialize_alert

    return serialize_alert(alert)
