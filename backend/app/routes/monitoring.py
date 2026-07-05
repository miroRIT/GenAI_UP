from fastapi import APIRouter

from app.services.monitoring_service import (
    get_disaster_map_layers,
    get_live_monitoring_feed,
    get_region_profile,
)
from app.services.geospatial_service import get_available_layers, get_district_geojson, get_mapped_incidents


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


@router.get("/geospatial/districts")
def geospatial_districts() -> dict[str, object]:
    return get_district_geojson()


@router.get("/geospatial/incidents")
def geospatial_incidents() -> list[dict[str, object]]:
    return get_mapped_incidents()


@router.get("/geospatial/layers")
def geospatial_layers() -> list[dict[str, object]]:
    return get_available_layers()
