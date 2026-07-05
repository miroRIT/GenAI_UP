from fastapi import APIRouter

from app.services.data_loader import load_all_data
from app.services.risk_engine import calculate_ward_risk_scores


router = APIRouter(tags=["overview"])


@router.get("/overview")
def overview() -> dict[str, object]:
    data = load_all_data()
    ward_scores = calculate_ward_risk_scores(data)

    return {
        "total_wards": int(len(data["wards"])),
        "total_complaints": int(len(data["citizen_complaints"])),
        "average_risk_score": round(float(ward_scores["community_risk_score"].mean()), 1),
        "high_risk_wards_count": int((ward_scores["risk_level"] == "High").sum()),
        "critical_risk_wards_count": int((ward_scores["risk_level"] == "Critical").sum()),
        "average_aqi": round(float(data["air_quality"]["aqi"].mean()), 1),
        "total_utility_outages": int(len(data["utility_outages"])),
        "total_emergency_incidents": int(len(data["emergency_incidents"])),
    }
