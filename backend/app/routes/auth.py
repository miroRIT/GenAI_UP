from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.services.auth_service import authenticate_user, create_access_token, decode_access_token, get_password_hash


router = APIRouter(tags=["auth"])
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "Viewer"
    district_id: str | None = None


@router.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": serialize_user(user)}


@router.post("/auth/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=409, detail="User already exists.")
    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=request.role,
        district_id=request.district_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.get("/auth/me")
def me(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token.")
    payload = decode_access_token(credentials.credentials)
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return serialize_user(user)


@router.post("/auth/logout")
def logout() -> dict[str, str]:
    return {"message": "Client should discard the token."}


def serialize_user(user: User) -> dict[str, object]:
    return {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "district_id": user.district_id,
    }
