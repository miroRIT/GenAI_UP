from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.security.permissions import require_auth
from app.services.job_service import job_status, run_job


router = APIRouter(tags=["jobs"])


@router.get("/jobs/status")
def status(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return job_status(db)


@router.get("/jobs/logs")
def logs(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return job_status(db)


@router.get("/jobs/health")
def health(db: Session = Depends(get_db)) -> dict[str, object]:
    logs = job_status(db)
    failures = [log for log in logs if log["status"] == "Failed"]
    return {
        "status": "degraded" if failures else "ok",
        "recent_jobs": len(logs),
        "recent_failures": len(failures),
    }


@router.post("/jobs/run/{job_name}")
def run(
    job_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict[str, object]:
    _require_job_permission(user, job_name)
    try:
        return run_job(db, job_name, triggered_by=user.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _require_job_permission(user: User, job_name: str) -> None:
    if user.role == "Admin":
        return
    if user.role == "Analyst" and job_name == "risk":
        return
    raise HTTPException(status_code=403, detail="Insufficient permissions to run this job.")
