from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

DEMO_USERS = [
    ("admin@civiciq.demo", "Admin@123", "Admin User", "Admin", None, "Platform Operations"),
    ("officer@civiciq.demo", "Officer@123", "District Officer", "District Officer", "NCR01", "District Administration"),
    ("department@civiciq.demo", "Department@123", "Fire Department User", "Department User", "NCR01", "Fire Department"),
    ("analyst@civiciq.demo", "Analyst@123", "Data Analyst", "Analyst", None, "Analytics Cell"),
    ("viewer@civiciq.demo", "Viewer@123", "Read Only Viewer", "Viewer", None, "Public Viewer"),
]


ROLE_PERMISSIONS = {
    "Admin": ["*"],
    "District Officer": ["alerts:assign", "alerts:update", "alerts:export", "districts:read"],
    "Department User": ["alerts:update", "districts:read"],
    "Analyst": ["analytics:read", "jobs:run", "reports:export"],
    "Viewer": ["read"],
}


def seed_demo_users(db: Session) -> None:
    for email, password, full_name, role, district_id, department in DEMO_USERS:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            existing.full_name = full_name
            existing.role = role
            existing.district_id = district_id
            existing.department = department
            existing.assigned_districts = f'["{district_id}"]' if district_id else "[]"
            existing.is_active = 1
            existing.hashed_password = get_password_hash(password)
            continue
        db.add(
            User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                role=role,
                district_id=district_id,
                department=department,
                assigned_districts=f'["{district_id}"]' if district_id else "[]",
            )
        )
    db.commit()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(user: User) -> str:
    settings = get_settings()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": user.email,
        "role": user.role,
        "district_id": user.district_id,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
