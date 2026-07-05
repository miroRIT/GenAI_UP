from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.observation_service import list_observations


router = APIRouter(tags=["observations"])


@router.get("/observations")
def observations(
    type: str = Query(..., pattern="^(weather|traffic|news|aqi)$"),
    district_id: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    return list_observations(db, type, district_id, limit)
