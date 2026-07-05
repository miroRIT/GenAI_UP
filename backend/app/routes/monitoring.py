from fastapi import APIRouter

from app.services.monitoring_service import (
    get_disaster_map_layers,
    get_live_monitoring_feed,
    get_region_profile,
)


router = APIRouter(tags=["monitoring"])


@router.get("/region/profile")
def region_profile() -> dict[str, object]:
    return get_region_profile()


@router.get("/geospatial/disaster-map")
def disaster_map() -> dict[str, object]:
    return get_disaster_map_layers()


@router.get("/monitoring/live")
def live_monitoring() -> dict[str, object]:
    return get_live_monitoring_feed()
