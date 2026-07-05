from fastapi import APIRouter

from app.services.data_loader import load_all_data
from app.services.recommendation_engine import generate_recommendations
from app.services.risk_engine import calculate_ward_risk_scores


router = APIRouter(tags=["recommendations"])


@router.get("/recommendations")
def recommendations() -> list[dict[str, object]]:
    data = load_all_data()
    scores = calculate_ward_risk_scores(data)
    return generate_recommendations(data, scores)
