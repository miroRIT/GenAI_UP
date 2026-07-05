from fastapi import APIRouter, HTTPException

from app.services.data_loader import load_all_data
from app.services.recommendation_engine import get_recommendations_for_ward
from app.services.risk_engine import calculate_ward_risk_scores, get_ward_detail


router = APIRouter(tags=["wards"])


@router.get("/wards")
def wards() -> list[dict[str, object]]:
    data = load_all_data()
    return calculate_ward_risk_scores(data).to_dict(orient="records")


@router.get("/wards/{ward_id}")
def ward_detail(ward_id: str) -> dict[str, object]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    detail = get_ward_detail(data, scores, ward_id)

    if detail is None:
        raise HTTPException(status_code=404, detail=f"Ward {ward_id} was not found.")

    detail["recommendations"] = get_recommendations_for_ward(detail)
    return detail
