from fastapi import APIRouter, HTTPException

from app.services.disaster_risk_engine import (
    calculate_disaster_risk,
    get_disaster_risk_for_district,
    get_disaster_risk_type,
)


router = APIRouter(tags=["disaster-risk"])


@router.get("/disaster-risk")
def disaster_risk() -> list[dict[str, object]]:
    return calculate_disaster_risk()


@router.get("/disaster-risk/{district_id}")
def district_disaster_risk(district_id: str) -> dict[str, object]:
    risk = get_disaster_risk_for_district(district_id)
    if not risk:
        raise HTTPException(status_code=404, detail="District not found.")
    return risk


@router.get("/disaster-risk/{district_id}/{risk_type}")
def district_disaster_risk_type(district_id: str, risk_type: str) -> dict[str, object]:
    risk = get_disaster_risk_type(district_id, risk_type)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk type or district not found.")
    return risk
