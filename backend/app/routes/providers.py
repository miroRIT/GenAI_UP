from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.permissions import require_permissions
from app.services.provider_status_service import get_provider_status, test_all_providers, test_provider


router = APIRouter(tags=["providers"])


@router.get("/providers/status")
def provider_status(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return get_provider_status(db)


@router.post("/providers/test/{provider_type}")
def provider_test(
    provider_type: str,
    db: Session = Depends(get_db),
    _user=Depends(require_permissions("providers:read")),
) -> dict[str, object]:
    if provider_type == "all":
        return test_all_providers(db)
    try:
        return test_provider(db, provider_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
