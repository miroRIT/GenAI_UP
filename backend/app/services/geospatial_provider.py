from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import BoundarySource
from app.services.geospatial_service import build_district_geojson


REQUIRED_PROPERTIES = {"district_id", "district_name", "state", "source_name"}


def official_backend_dir() -> Path:
    path = get_settings().geojson_dir / "official"
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_boundary_sources(db: Session) -> list[dict[str, Any]]:
    ensure_boundary_sources(db)
    return [
        {
            "source_name": source.source_name,
            "source_url": source.source_url,
            "license": source.license,
            "downloaded_at": source.downloaded_at.isoformat(),
            "boundary_level": source.boundary_level,
            "state": source.state,
            "district_name": source.district_name,
            "file_path": source.file_path,
            "is_official": bool(source.is_official),
        }
        for source in db.query(BoundarySource).order_by(BoundarySource.is_official.desc(), BoundarySource.source_name).all()
    ]


def load_district_boundaries(db: Session, source: str = "auto") -> dict[str, Any]:
    ensure_boundary_sources(db)
    official = _find_official_geojson()
    if source == "official" and official:
        return _load_and_mark(official, True)
    if source == "official" and not official:
        return _fallback_geojson()
    if official:
        return _load_and_mark(official, True)
    return _fallback_geojson()


def reload_boundaries(db: Session) -> dict[str, Any]:
    db.query(BoundarySource).delete()
    db.commit()
    ensure_boundary_sources(db)
    return {"sources": list_boundary_sources(db)}


def ensure_boundary_sources(db: Session) -> None:
    if db.query(BoundarySource).count() > 0:
        return
    official = _find_official_geojson()
    if official:
        metadata = _read_metadata(official)
        db.add(
            BoundarySource(
                source_name=metadata.get("source_name", "Official NCR Boundary"),
                source_url=metadata.get("source_url", ""),
                license=metadata.get("license", "Unknown"),
                downloaded_at=datetime.utcnow(),
                boundary_level=metadata.get("boundary_level", "district"),
                state=metadata.get("state", "NCR"),
                district_name=metadata.get("district_name", "NCR"),
                file_path=str(official),
                is_official=1 if metadata.get("is_official", True) else 0,
            )
        )
    else:
        fallback_path = get_settings().geojson_dir / "ncr_districts.geojson"
        if not fallback_path.exists():
            fallback_path.write_text(json.dumps(build_district_geojson(), indent=2), encoding="utf-8")
        db.add(
            BoundarySource(
                source_name="CivicIQ simplified NCR demo boundaries",
                source_url="local generated sample",
                license="Demo only",
                boundary_level="district",
                state="NCR",
                district_name="NCR",
                file_path=str(fallback_path),
                is_official=0,
            )
        )
    db.commit()


def validate_geojson(geojson: dict[str, Any]) -> list[str]:
    errors = []
    features = geojson.get("features", [])
    if not features:
        return ["GeoJSON has no features."]
    for index, feature in enumerate(features):
        properties = feature.get("properties", {})
        missing = REQUIRED_PROPERTIES - set(properties)
        if missing:
            errors.append(f"Feature {index} missing properties: {', '.join(sorted(missing))}")
        geometry = feature.get("geometry", {})
        if not geometry.get("coordinates"):
            errors.append(f"Feature {index} has empty coordinates.")
    district_names = {feature.get("properties", {}).get("district_name") for feature in features}
    required_core = {"Delhi NCT", "Gurugram", "Ghaziabad", "Gautam Buddh Nagar / Noida", "Faridabad", "Meerut"}
    missing_core = required_core - district_names
    if missing_core:
        errors.append(f"Boundary coverage missing core NCR districts: {', '.join(sorted(missing_core))}")
    return errors


def copy_official_to_frontend() -> None:
    official = _find_official_geojson()
    if not official:
        return
    frontend_path = Path(__file__).resolve().parents[3] / "frontend" / "public" / "geojson" / "official"
    frontend_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(official, frontend_path / official.name)


def _find_official_geojson() -> Path | None:
    candidates = sorted(official_backend_dir().glob("*.geojson")) + sorted(official_backend_dir().glob("*.json"))
    return candidates[0] if candidates else None


def _load_and_mark(path: Path, is_official: bool) -> dict[str, Any]:
    geojson = json.loads(path.read_text(encoding="utf-8"))
    for feature in geojson.get("features", []):
        feature.setdefault("properties", {})
        feature["properties"].setdefault("source_name", path.stem)
        feature["properties"]["is_official"] = is_official
    geojson["metadata"] = {
        "source_name": path.stem,
        "license": _read_metadata(path).get("license", "Unknown"),
        "is_official": is_official,
        "file_path": str(path),
        "validation_errors": validate_geojson(geojson),
    }
    return geojson


def _fallback_geojson() -> dict[str, Any]:
    geojson = build_district_geojson()
    for feature in geojson.get("features", []):
        feature["properties"]["source_name"] = "CivicIQ simplified NCR demo boundaries"
        feature["properties"]["is_official"] = False
    geojson["metadata"] = {
        "source_name": "CivicIQ simplified NCR demo boundaries",
        "license": "Demo only",
        "is_official": False,
        "validation_errors": validate_geojson(geojson),
    }
    return geojson


def _read_metadata(path: Path) -> dict[str, Any]:
    metadata_path = path.with_suffix(".metadata.json")
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    return {}
