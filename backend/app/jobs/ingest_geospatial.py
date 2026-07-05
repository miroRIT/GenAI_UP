from app.services.geospatial_service import ensure_geojson


def run() -> int:
    ensure_geojson()
    return 1
