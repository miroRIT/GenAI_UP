from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.job_service import job_status, run_job


router = APIRouter(tags=["jobs"])


@router.get("/jobs/status")
def status(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return job_status(db)


@router.post("/jobs/run/{job_name}")
def run(job_name: str, db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        return run_job(db, job_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
