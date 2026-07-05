from fastapi import APIRouter, Depends

from app.services.monitoring_service import (
    get_disaster_map_layers,
    get_live_monitoring_feed,
    get_region_profile,
)
from app.services.geospatial_service import get_available_layers, get_district_geojson, get_mapped_incidents
from app.services.geospatial_provider import list_boundary_sources, load_district_boundaries, reload_boundaries
from app.database import get_db
from app.security.permissions import require_permissions
from sqlalchemy.orm import Session


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
def geospatial_districts(source: str = "auto", db: Session = Depends(get_db)) -> dict[str, object]:
    if source in {"official", "auto"}:
        return load_district_boundaries(db, source)
    return get_district_geojson()


@router.get("/geospatial/incidents")
def geospatial_incidents() -> list[dict[str, object]]:
    return get_mapped_incidents()


@router.get("/geospatial/layers")
def geospatial_layers() -> list[dict[str, object]]:
    return get_available_layers()


@router.get("/geospatial/boundary-sources")
def boundary_sources(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return list_boundary_sources(db)


@router.post("/geospatial/reload-boundaries")
def reload_geospatial_boundaries(
    db: Session = Depends(get_db),
    _user=Depends(require_permissions("*")),
) -> dict[str, object]:
    return reload_boundaries(db)
