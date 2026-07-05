from __future__ import annotations

from typing import Callable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.db_models import Alert, User


PERMISSIONS = {
    "Admin": {"*"},
    "District Officer": {
        "districts:read",
        "alerts:read",
        "alerts:assign",
        "alerts:acknowledge",
        "alerts:resolve",
        "alerts:export",
    },
    "Department User": {
        "alerts:read_assigned",
        "alerts:notes",
        "alerts:progress",
        "alerts:resolve_assigned",
    },
    "Analyst": {
        "analytics:read",
        "providers:read",
        "jobs:run_analytics",
        "reports:export",
        "alerts:notes",
    },
    "Viewer": {"read"},
}

security = HTTPBearer(auto_error=False)


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required.")
    try:
        payload = jwt.decode(
            credentials.credentials,
            get_settings().jwt_secret_key,
            algorithms=[get_settings().jwt_algorithm],
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token.") from exc
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or missing user.")
    return user


def has_permission(user: User, permission: str) -> bool:
    role_permissions = PERMISSIONS.get(user.role, set())
    return "*" in role_permissions or permission in role_permissions


def require_roles(*roles: str) -> Callable[[User], User]:
    def dependency(user: User = Depends(require_auth)) -> User:
        if user.role not in roles and user.role != "Admin":
            raise HTTPException(status_code=403, detail="Insufficient role.")
        return user

    return dependency


def require_permissions(*permissions: str) -> Callable[[User], User]:
    def dependency(user: User = Depends(require_auth)) -> User:
        if user.role == "Admin":
            return user
        if not all(has_permission(user, permission) for permission in permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return user

    return dependency


def require_district_access(user: User, district_id: str) -> None:
    if user.role in {"Admin", "Analyst", "Viewer"}:
        return
    assigned = set(_assigned_districts(user))
    if district_id != user.district_id and district_id not in assigned:
        raise HTTPException(status_code=403, detail="District out of scope.")


def require_alert_access(user: User, alert: Alert, action: str = "read") -> None:
    if user.role == "Admin":
        return
    if user.role == "Viewer":
        if action == "read":
            return
        raise HTTPException(status_code=403, detail="Viewer cannot modify or export alerts.")
    if user.role == "Analyst":
        if action in {"read", "notes", "export"}:
            return
        raise HTTPException(status_code=403, detail="Analyst cannot modify alerts.")
    if user.role == "District Officer":
        require_district_access(user, alert.district_id)
        if action in {"read", "assign", "acknowledge", "resolve", "export", "notes"}:
            return
    if user.role == "Department User":
        if alert.assigned_department == user.department and action in {"read", "notes", "progress", "resolve", "export"}:
            return
        raise HTTPException(status_code=403, detail="Department user can only access assigned alerts.")
    raise HTTPException(status_code=403, detail="Alert access denied.")


def _assigned_districts(user: User) -> list[str]:
    import json

    try:
        return json.loads(user.assigned_districts or "[]")
    except Exception:
        return []
