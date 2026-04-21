"""
Authentication routes: /api/auth/register  and  /api/auth/login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.database import get_db, User
from backend.utils.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    city: Optional[str] = None
    age_group: Optional[str] = None        # <18 | 18-30 | 30-45 | 45-60 | 60+
    health_condition: Optional[str] = None  # normal | asthma | elderly


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    city: Optional[str]
    age_group: Optional[str]
    health_condition: Optional[str]

    class Config:
        from_attributes = True


# ── Register ──────────────────────────────────────────────────────────────────
@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        city=payload.city,
        age_group=payload.age_group,
        health_condition=payload.health_condition,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.from_orm(user)}


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.from_orm(user)}


# ── Me (optional – useful later) ──────────────────────────────────────────────
@router.get("/me")
def get_me(db: Session = Depends(get_db)):
    """Placeholder – wire up JWT middleware when needed."""
    return {"detail": "Attach Authorization: Bearer <token> to use this endpoint."}