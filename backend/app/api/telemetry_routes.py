from fastapi import APIRouter

from app.services.mock_data_service import generate_city_telemetry, summarize_city_conditions


router = APIRouter(tags=["telemetry"])


@router.get("/telemetry/live")
def get_live_telemetry() -> dict[str, object]:
    records = generate_city_telemetry()
    return {
        "records": records,
        "summary": summarize_city_conditions(records),
    }
