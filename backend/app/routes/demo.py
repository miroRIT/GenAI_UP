from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.demo_scenario_service import (
    audit_logs,
    demo_dashboard_overview,
    demo_recommendations,
    explain_recommendation,
    export_brief,
    exports_list,
    map_layers,
    operations_snapshot,
    refresh_demo_feeds,
    reset_demo_runtime,
    run_crisis_demo,
)


router = APIRouter(tags=["demo"])


@router.get("/dashboard/overview")
def dashboard_overview() -> dict[str, object]:
    return demo_dashboard_overview()


@router.post("/demo/seed")
def seed_demo() -> dict[str, object]:
    return reset_demo_runtime()


@router.post("/demo/run-crisis")
def run_crisis(
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return run_crisis_demo(db, actor="demo-operator")


@router.post("/jobs/refresh-demo-feeds")
def refresh_feeds() -> dict[str, object]:
    return refresh_demo_feeds()


@router.get("/recommendations/{recommendation_id}/explain")
def recommendation_explain(recommendation_id: str) -> dict[str, object]:
    explanation = explain_recommendation(recommendation_id)
    if not explanation:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    return explanation


@router.get("/demo/recommendations")
def demo_recs() -> list[dict[str, object]]:
    return demo_recommendations()


@router.get("/providers/health")
def providers_health() -> dict[str, object]:
    return operations_snapshot()


@router.get("/operations")
def operations() -> dict[str, object]:
    return operations_snapshot()


@router.get("/audit-logs")
def audit() -> list[dict[str, object]]:
    return audit_logs()


@router.get("/map/layers")
def map_layer_payload() -> dict[str, object]:
    return map_layers()


@router.get("/map/incidents")
def map_incidents() -> list[dict[str, object]]:
    return map_layers()["incidents"]


@router.get("/exports")
def exports() -> list[dict[str, object]]:
    return exports_list()


@router.get("/exports/{export_id}")
def export_download(export_id: str) -> Response:
    brief = export_brief(export_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Export not found.")
    return Response(
        content=brief,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{export_id}-civiciq-brief.md"'},
    )
