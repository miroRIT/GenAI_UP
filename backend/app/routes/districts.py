from fastapi import APIRouter, HTTPException

from app.services.alert_service import list_alerts
from app.database import SessionLocal
from app.services.data_loader import load_all_data
from app.services.disaster_risk_engine import get_disaster_risk_for_district
from app.services.forecast_engine import generate_forecast
from app.services.geospatial_service import get_mapped_incidents
from app.services.provider_service import fetch_traffic_observations, fetch_weather_observations, fetch_environmental_observations
from app.services.recommendation_engine import get_recommendations_for_ward
from app.services.risk_engine import calculate_ward_risk_scores


router = APIRouter(tags=["districts"])


@router.get("/districts")
def districts() -> list[dict[str, object]]:
    return calculate_ward_risk_scores(load_all_data()).to_dict(orient="records")


@router.get("/districts/{district_id}")
def district_detail(district_id: str) -> dict[str, object]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    match = scores[scores["ward_id"] == district_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="District not found.")
    district = match.iloc[0].to_dict()
    district["disaster_risk"] = get_disaster_risk_for_district(district_id)
    district["weather"] = _match(fetch_weather_observations(), district_id)
    district["traffic"] = _match(fetch_traffic_observations(), district_id)
    district["environment"] = _match(fetch_environmental_observations(), district_id)
    district["incidents"] = [item for item in get_mapped_incidents() if item["district_id"] == district_id]
    district["recommendations"] = get_recommendations_for_ward(district)
    db = SessionLocal()
    try:
        district["alerts"] = [item for item in list_alerts(db) if item["district_id"] == district_id]
    finally:
        db.close()
    return district


@router.get("/districts/{district_id}/risk")
def district_risk(district_id: str) -> dict[str, object]:
    risk = get_disaster_risk_for_district(district_id)
    if not risk:
        raise HTTPException(status_code=404, detail="District not found.")
    return risk


@router.get("/districts/{district_id}/alerts")
def district_alerts(district_id: str) -> list[dict[str, object]]:
    db = SessionLocal()
    try:
        return [item for item in list_alerts(db) if item["district_id"] == district_id]
    finally:
        db.close()


@router.get("/districts/{district_id}/recommendations")
def district_recommendations(district_id: str) -> list[str]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    match = scores[scores["ward_id"] == district_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="District not found.")
    return get_recommendations_for_ward(match.iloc[0].to_dict())


@router.get("/districts/{district_id}/incidents")
def district_incidents(district_id: str) -> list[dict[str, object]]:
    return [item for item in get_mapped_incidents() if item["district_id"] == district_id]


@router.get("/districts/{district_id}/forecast")
def district_forecast(district_id: str) -> dict[str, object]:
    return {
        "district_id": district_id,
        "complaints": generate_forecast(load_all_data(), "complaints", 5),
        "aqi": generate_forecast(load_all_data(), "aqi", 5),
        "outages": generate_forecast(load_all_data(), "outages", 5),
    }


def _match(records: list[dict[str, object]], district_id: str) -> dict[str, object]:
    return next((record for record in records if record["district_id"] == district_id), {})
