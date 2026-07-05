from fastapi import APIRouter, Query

from app.services.anomaly_engine import detect_anomalies
from app.services.data_loader import load_all_data
from app.services.forecast_engine import generate_forecast
from app.services.risk_engine import calculate_ward_risk_scores


router = APIRouter(tags=["analytics"])


@router.get("/analytics/risk-ranking")
def risk_ranking() -> list[dict[str, object]]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    return scores.sort_values("community_risk_score", ascending=False).to_dict(orient="records")


@router.get("/analytics/anomalies")
def anomalies() -> list[dict[str, object]]:
    return detect_anomalies(load_all_data())


@router.get("/analytics/forecast")
def forecast(
    metric: str = Query("complaints", pattern="^(complaints|aqi|outages)$"),
    periods: int = Query(7, ge=1, le=30),
) -> dict[str, object]:
    return generate_forecast(load_all_data(), metric=metric, periods=periods)
